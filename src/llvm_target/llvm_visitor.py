# src/llvm_target/llvm_visitor.py

from ..parser.ast_nodes import (
    LiteralNode, BinaryOpNode, UnaryOpNode,
    VariableNode, VarDeclNode, AssignNode,
    CastNode, TypeNode, BlockNode, ProgramNode,
    CommentNode, ArrayDeclNode, ArrayInitNode,
    ArrayAccessNode, StringLiteralNode,
    FunctionCallNode, IncludeNode,
    EnumDefNode, IfNode, WhileNode, BreakNode, ContinueNode, ScopeNode,
    # Assignment 5 (nieuw):
    ParamNode, FunctionDeclNode, FunctionDefNode,
    ReturnNode, DefineNode, IncludeFileNode,
)


class LLVMVisitor:
    """
    Genereert LLVM IR code vanuit de AST.

    Structuur van de gegenereerde output:
      1. Globale string constanten (@.str.0, @.str.1, ...)
      2. Functie declaraties (declare i32 @printf(...))
      3. De main functie: define i32 @main() { ... }

    Elke visit methode die een expressie bezoekt geeft een tuple terug:
      (llvm_value, llvm_type)
        llvm_value: een register (%t0) of een directe waarde (42, 3.14)
        llvm_type:  het LLVM type van die waarde (i32, float, i8*, enz.)

    Lvalues (linkerkant van assignment) worden verwerkt via _get_address(),
    die een (adres_register, pointer_type) tuple teruggeeft.
    """

    def __init__(self):
        self.globals            = []        # globale string constanten
        self.func_decls         = set()     # printf / scanf declaraties nodig?
        self.instructions       = []        # instructies in de HUIDIGE functie-body
        self.reg_counter        = 0         # teller voor %t0, %t1, ... (globaal)
        self.str_counter        = 0         # teller voor @.str.0, @.str.1, ...
        self.string_cache       = {}        # raw_value → global_name (geen duplicaten)
        self.var_info           = {}        # naam → dict met type info
        self.stdio_included     = False
        self.label_counter      = 0         # unieke teller voor if/while labels
        self.loop_stack         = []        # stack van (break_label, continue_label)
        self._block_terminated  = False     # True na br/ret → geen dubbele terminator
        self.scope_stack        = [{}]      # stack van {original_name: llvm_name} per scope
        self.name_counter       = {}        # original_name → aantal keer gedeclareerd

        # Assignment 5 nieuw:
        self.functions          = []
        self.func_return_types  = {}
        self.current_func_name  = None
        self.global_var_info    = {}        # naam → info dict voor GLOBALE variabelen (@ prefix)

        # Optimalisatie: set van variabelenamen die gelezen worden in de huidige functie.
        # None = uitgeschakeld. Gezet door visitFunctionDef vóór body-generatie.
        self._current_used_vars: set = None

    # ============================================================
    # HELPERS: registers, types, strings
    # ============================================================

    def new_reg(self) -> str:
        """Geeft een nieuw uniek tijdelijk register terug: %t0, %t1, ..."""
        r = f"%t{self.reg_counter}"
        self.reg_counter += 1
        return r

    def emit(self, instr: str):
        """Voeg een instructie toe aan de main body (met 2 spaties inspringing)."""
        self.instructions.append(f"  {instr}")

    def emit_comment(self, text: str):
        """
        Zet een C comment om naar een LLVM comment (begint met ';').
        Multi-line block comments worden per regel uitgestoten.
        """
        if text.startswith('//'):
            # line comment: verwijder '//' prefix
            self.instructions.append(f"  ; {text[2:].strip()}")
        elif text.startswith('/*'):
            # block comment: verwijder '/*' en '*/' en split op newlines
            inner = text[2:-2].strip()
            for line in inner.split('\n'):
                stripped = line.strip().lstrip('*').strip()
                if stripped:
                    self.instructions.append(f"  ; {stripped}")

    def _stmt_to_c(self, node) -> str:
        """
        Vertaalt een statement-AST-node terug naar een korte, leesbare C-string.
        Wordt gebruikt als commentaar na de eerste LLVM-instructie van dat statement.

        Geeft een lege string terug voor CommentNode (die heeft al zijn eigen comment).
        Voor complexe nodes (if/while) houden we het bij de eerste regel, geen body.
        """
        from ..parser.ast_nodes import (
            VarDeclNode, ArrayDeclNode, AssignNode, FunctionCallNode,
            ReturnNode, BreakNode, ContinueNode, CommentNode,
            IfNode, WhileNode, ScopeNode, EnumDefNode,
            VariableNode, LiteralNode, BinaryOpNode, UnaryOpNode,
            StringLiteralNode, ArrayAccessNode, CastNode,
        )

        def expr_to_c(e) -> str:
            """Recursief een expressie omzetten naar C-string (beknopt)."""
            if e is None:
                return ''
            if isinstance(e, LiteralNode):
                if e.type_name == 'char':
                    if isinstance(e.value, str):
                        return f"'{e.value}'"
                    return f"'\\x{e.value:02x}'"
                return str(e.value)
            if isinstance(e, StringLiteralNode):
                return f'"{e.value[:20]}"'
            if isinstance(e, VariableNode):
                return e.name
            if isinstance(e, BinaryOpNode):
                return f'{expr_to_c(e.left)} {e.op} {expr_to_c(e.right)}'
            if isinstance(e, UnaryOpNode):
                if e.op in ('suffix++', 'suffix--'):
                    return f'{expr_to_c(e.operand)}{e.op[6:]}'
                if e.op in ('prefix++', 'prefix--'):
                    return f'{e.op[6:]}{expr_to_c(e.operand)}'
                return f'{e.op}{expr_to_c(e.operand)}'
            if isinstance(e, ArrayAccessNode):
                return f'{expr_to_c(e.array_expr)}[{expr_to_c(e.index)}]'
            if isinstance(e, CastNode):
                t = e.target_type
                return f'({t.base_type}{"*"*t.pointer_depth}){expr_to_c(e.operand)}'
            if isinstance(e, FunctionCallNode):
                args = ', '.join(expr_to_c(a) for a in e.args[:3])
                suffix = ', ...' if len(e.args) > 3 else ''
                return f'{e.name}({args}{suffix})'
            return '...'

        def type_to_c(t) -> str:
            const = 'const ' if t.is_const else ''
            stars = '*' * t.pointer_depth
            return f'{const}{t.base_type}{stars}'

        if isinstance(node, CommentNode):
            return ''  # al apart afgehandeld via visitComment

        if isinstance(node, VarDeclNode):
            t = type_to_c(node.var_type)
            val = f' = {expr_to_c(node.value)}' if node.value else ''
            return f'{t} {node.name}{val};'

        if isinstance(node, ArrayDeclNode):
            t = type_to_c(node.var_type)
            dims = ''.join(f'[{d}]' for d in node.dimensions)
            return f'{t} {node.name}{dims};'

        if isinstance(node, AssignNode):
            return f'{expr_to_c(node.target)} = {expr_to_c(node.value)};'

        if isinstance(node, FunctionCallNode):
            return f'{expr_to_c(node)};'

        if isinstance(node, ReturnNode):
            if node.value is None:
                return 'return;'
            return f'return {expr_to_c(node.value)};'

        if isinstance(node, BreakNode):
            return 'break;'

        if isinstance(node, ContinueNode):
            return 'continue;'

        if isinstance(node, IfNode):
            return f'if ({expr_to_c(node.condition)}) {{ ... }}'

        if isinstance(node, WhileNode):
            return f'while ({expr_to_c(node.condition)}) {{ ... }}'

        if isinstance(node, ScopeNode):
            return '{ ... }'

        if isinstance(node, EnumDefNode):
            return f'enum {node.name} {{ ... }};'

        # expressie als statement (bv. i++ als losse regel)
        return f'{expr_to_c(node)};'

    def llvm_base_type(self, base_type: str) -> str:
        """Zet een C basistype om naar een LLVM type string."""
        return {'int': 'i32', 'float': 'float', 'char': 'i8'}.get(base_type, 'i32')

    def llvm_type(self, base_type: str, pointer_depth: int = 0) -> str:
        """
        Zet een C type (inclusief pointer diepte) om naar LLVM type string.
        Voorbeelden:
          int        → i32
          float*     → float*
          char**     → i8**
        """
        base = self.llvm_base_type(base_type)
        return base + '*' * pointer_depth

    def llvm_array_type(self, base_type: str, dimensions: list) -> str:
        """
        Bouwt het LLVM type voor een array.
        Voorbeelden:
          int[3]     → [3 x i32]
          int[2][3]  → [2 x [3 x i32]]
        """
        t = self.llvm_base_type(base_type)
        for d in reversed(dimensions):
            t = f"[{d} x {t}]"
        return t

    def get_string_global(self, raw_value: str) -> str:
        """
        Geeft de naam van een globale string constante terug.
        Maakt een nieuwe aan als die nog niet bestaat (string deduplicatie).

        EDGE CASE: lege string "" → length = 1 (alleen null terminator)
        EDGE CASE: escape sequences worden omgezet naar LLVM hex notatie:
          \\n → \\0A, \\t → \\09, \\\\ → \\5C, \\" → \\22
        """
        if raw_value in self.string_cache:
            return self.string_cache[raw_value]

        name = f"@.str.{self.str_counter}"
        self.str_counter += 1
        self.string_cache[raw_value] = name

        llvm_str = self._to_llvm_string(raw_value)
        length   = self._string_byte_length(raw_value) + 1  # +1 voor null terminator

        self.globals.append(
            f'{name} = private unnamed_addr constant [{length} x i8] c"{llvm_str}\\00"'
        )
        return name

    def _to_llvm_string(self, s: str) -> str:
        """
        Zet een Python string (met escape sequences als \\n, \\t) om naar
        de LLVM string notatie (\\0A, \\09, enz.).

        EDGE CASE: de string die de visitor ontvangt bevat LETTERLIJKE backslash-n
        (twee tekens: \\ en n), niet een echte newline. Dat is hoe de CST visitor
        het opslaat. We moeten dus \\n (2 tekens) → \\0A omzetten.
        """
        result = ''
        i = 0
        while i < len(s):
            c = s[i]
            if c == '\\' and i + 1 < len(s):
                nc = s[i + 1]
                escape_map = {
                    'n': '\\0A', 't': '\\09', 'r': '\\0D',
                    '\\': '\\5C', '"': '\\22', '0': '\\00',
                    'b': '\\08', 'f': '\\0C'
                }
                if nc in escape_map:
                    result += escape_map[nc]
                else:
                    result += c + nc
                i += 2
            elif c == '"':
                result += '\\22'
                i += 1
            elif ord(c) < 32 or ord(c) > 126:
                result += f'\\{ord(c):02X}'
                i += 1
            else:
                result += c
                i += 1
        return result

    def _string_byte_length(self, s: str) -> int:
        """
        Berekent het aantal bytes van een string in geheugen
        (escape sequences tellen als 1 byte).
        """
        length = 0
        i = 0
        while i < len(s):
            if s[i] == '\\' and i + 1 < len(s):
                i += 2
            else:
                i += 1
            length += 1
        return length

    def finalize(self) -> str:
        """
        Assembleer de volledige LLVM IR output en geef als string terug.

        Volgorde:
          1. Globale string constanten
          2. Externe declaraties (printf, scanf, user forward decls)
          3. Alle functiedefinities in volgorde
        """
        lines = []

        # globale string constanten
        for g in self.globals:
            lines.append(g)
        if self.globals:
            lines.append('')

        # externe functie declaraties
        if 'printf' in self.func_decls:
            lines.append('declare i32 @printf(i8*, ...)')
        if 'scanf' in self.func_decls:
            lines.append('declare i32 @scanf(i8*, ...)')
        if 'malloc' in self.func_decls:
            lines.append('declare i8* @malloc(i64)')
        if 'free' in self.func_decls:
            lines.append('declare void @free(i8*)')
        # user forward declarations (functies zonder body)
        for decl_line in self.func_decls:
            if decl_line not in ('printf', 'scanf') and decl_line.startswith('declare '):
                lines.append(decl_line)
        if self.func_decls:
            lines.append('')

        # alle functiedefinities
        for func_lines in self.functions:
            lines.extend(func_lines)
            lines.append('')

        return '\n'.join(lines).rstrip() + '\n'

    # ============================================================
    # TYPE COERCERING
    # ============================================================

    def _common_type(self, t1: str, t2: str) -> str:
        """Bepaal het rijkste type voor een binaire operatie."""
        if t1 == 'float' or t2 == 'float':
            return 'float'
        if t1 == 'i32' or t2 == 'i32':
            return 'i32'
        return 'i8'

    def _coerce(self, value: str, from_type: str, to_type: str) -> str:
        """
        Emitteer een type conversie instructie als nodig.
        Geeft de (mogelijk nieuwe) register naam terug.

        EDGE CASE: from_type == to_type → geen instructie, direct teruggeven
        EDGE CASE: float → i8: twee stappen (float→i32→i8)
        """
        if from_type == to_type:
            return value

        reg = self.new_reg()

        if from_type == 'float' and to_type == 'i32':
            self.emit(f"{reg} = fptosi float {value} to i32")
        elif from_type == 'i32' and to_type == 'float':
            self.emit(f"{reg} = sitofp i32 {value} to float")
        elif from_type == 'i8' and to_type == 'i32':
            self.emit(f"{reg} = sext i8 {value} to i32")
        elif from_type == 'i32' and to_type == 'i8':
            self.emit(f"{reg} = trunc i32 {value} to i8")
        elif from_type == 'i8' and to_type == 'float':
            tmp = self.new_reg()
            self.emit(f"{tmp} = sext i8 {value} to i32")
            self.emit(f"{reg} = sitofp i32 {tmp} to float")
        elif from_type == 'float' and to_type == 'i8':
            tmp = self.new_reg()
            self.emit(f"{tmp} = fptosi float {value} to i32")
            self.emit(f"{reg} = trunc i32 {tmp} to i8")
        elif from_type == 'i32' and to_type == 'i64':
            self.emit(f"{reg} = sext i32 {value} to i64")
        elif from_type == 'i8' and to_type == 'i64':
            self.emit(f"{reg} = sext i8 {value} to i64")
        elif from_type == 'i64' and to_type == 'i32':
            self.emit(f"{reg} = trunc i64 {value} to i32")
        else:
            # geen bekende conversie → ongewijzigd teruggeven
            return value

        return reg

    # ============================================================
    # SHADOWING HELPERS
    # ============================================================

    def _get_unique_llvm_name(self, name: str) -> str:
        """
        Geeft een unieke LLVM naam terug voor een variabele declaratie.

        Als 'name' nog niet bestaat → gebruik 'name' direct.
        Als 'name' al bestaat (shadowing in inner scope) → gebruik 'name.1', 'name.2', ...

        Voorbeeld:
          buitenste scope: int x  → llvm_name = 'x'
          binnenste scope: int x  → llvm_name = 'x.1'
          nog een scope:   int x  → llvm_name = 'x.2'
        """
        if name not in self.var_info:
            return name
        count = self.name_counter.get(name, 0) + 1
        self.name_counter[name] = count
        return f"{name}.{count}"

    def _lookup_llvm_name(self, name: str) -> str:
        """
        Zoek de huidige actieve LLVM naam voor een variabele.

        Doorzoekt de scope_stack van binnen naar buiten.
        De binnenste scope wint (shadowing).

        Voorbeeld:
          buitenste scope heeft x → 'x'
          binnenste scope heeft x → 'x.1'
          → binnen de binnenste scope geeft dit 'x.1' terug
          → buiten de binnenste scope geeft dit 'x' terug
        """
        for scope in reversed(self.scope_stack):
            if name in scope:
                return scope[name]
        return name  # fallback

    # ============================================================
    # ADRES BEREKENING (voor lvalues)
    # ============================================================

    def _get_address(self, node) -> tuple:
        """
        Berekent het adres (pointer) van een lvalue node.
        Geeft (adres_register, pointer_type) terug.

        Geldige lvalues:
          VariableNode       → %naam, type*
          ArrayAccessNode    → getelementptr, elem_type*
          UnaryOpNode('*')   → de waarde van de pointer IS het adres
        """
        if isinstance(node, VariableNode):
            llvm_name = self._lookup_llvm_name(node.name)
            info = self.var_info[llvm_name]
            prefix = '@' if info.get('is_global') else '%'
            if info['is_array']:
                array_t = self.llvm_array_type(info['base_type'], info['dimensions'])
                return (f"{prefix}{llvm_name}", f"{array_t}*")
            else:
                llvm_t = self.llvm_type(info['base_type'], info['pointer_depth'])
                return (f"{prefix}{llvm_name}", f"{llvm_t}*")

        elif isinstance(node, ArrayAccessNode):
            return self._get_array_element_address(node)

        elif isinstance(node, UnaryOpNode) and node.op == '*':
            # dereference als lvalue: *ptr = 5
            # het adres is de waarde van de pointer zelf
            ptr_val, ptr_type = node.operand.accept(self)
            return (ptr_val, ptr_type)

        raise ValueError(f"Kan geen adres berekenen voor: {node}")

    def _get_array_element_address(self, node: ArrayAccessNode) -> tuple:
        """
        Emitteer een getelementptr instructie voor arr[i] of arr[i][j].

        Aanpak voor arr[i][j]:
          ANTLR parseert dit als (arr[i])[j] → geneste ArrayAccessNode.
          We navigeren naar de base VariableNode en verzamelen alle
          indices onderweg (van buiten naar binnen, dan omdraaien).

        LLVM GEP: getelementptr [2 x [3 x i32]], [2 x [3 x i32]]* %matrix,
                                i32 0, i32 i, i32 j
          Eerste i32 0: pointer deref (van ptr naar array)
          Volgende indices: dimensies
        """
        indices = []
        current = node

        # verzamel indices van buiten naar binnen
        while isinstance(current, ArrayAccessNode):
            idx_val, idx_type = current.index.accept(self)
            idx_val = self._coerce(idx_val, idx_type, 'i32')
            indices.insert(0, idx_val)    # insert vooraan → van binnen naar buiten
            current = current.array_expr

        # current is nu de base VariableNode
        if not isinstance(current, VariableNode):
            raise ValueError(f"Onverwachte base in array access: {current}")

        name = current.name
        info = self.var_info[name]

        # ── POINTER INDEXERING: int* p; p[i] = *(p + i) ────────────────────
        # Een pointer (niet-array) variabele heeft is_array=False maar pointer_depth>0.
        # p[i] is dan identiek aan getelementptr T, T* %p_val, i32 i
        if not info['is_array'] and info['pointer_depth'] > 0:
            elem_t  = self.llvm_type(info['base_type'], info['pointer_depth'] - 1)
            ptr_t   = self.llvm_type(info['base_type'], info['pointer_depth'])
            llvm_nm = self._lookup_llvm_name(name)
            # load de pointer zelf
            ptr_load = self.new_reg()
            self.emit(f"{ptr_load} = load {ptr_t}, {ptr_t}* %{llvm_nm}")
            # decay naar elem_t pointer als ptr_t is een array type — niet nodig hier
            # voor elke dimensie in indices, stap op
            result_ptr = ptr_load
            for idx in indices:
                gep_reg = self.new_reg()
                self.emit(f"{gep_reg} = getelementptr {elem_t}, {ptr_t} {result_ptr}, i32 {idx}")
                result_ptr = gep_reg
            return (result_ptr, f"{elem_t}*")

        # ── ARRAY INDEXERING: normale [N x T]* GEP ──────────────────────────
        arr_t  = self.llvm_array_type(info['base_type'], info['dimensions'])
        elem_t = self.llvm_base_type(info['base_type'])

        # bouw de GEP index string: altijd beginnen met i32 0
        idx_str = 'i32 0, ' + ', '.join(f'i32 {idx}' for idx in indices)
        ptr_reg = self.new_reg()
        self.emit(f"{ptr_reg} = getelementptr {arr_t}, {arr_t}* %{name}, {idx_str}")

        return (ptr_reg, f"{elem_t}*")

    # ============================================================
    # STRUCTUUR
    # ============================================================

    def visitInclude(self, node):
        if node.header == 'stdio.h':
            self.stdio_included = True

    def visitBlock(self, node):
        self.scope_stack.append({})
        for stmt in node.statements:
            if self._block_terminated:
                break
            stmt.accept(self)
        self.scope_stack.pop()

    def visitComment(self, node):
        self.emit_comment(node.text)

    # ============================================================
    # DECLARATIES
    # ============================================================

    def _collect_used_vars(self, node, used: set, assign_target=False):
        """
        Loopt recursief door de AST en verzamelt de namen van alle variabelen
        die GELEZEN worden (niet alleen als assignment-target voorkomen).

        Parameters:
          node          — het te doorzoeken AST-node
          used          — de set waaraan gelezen namen worden toegevoegd
          assign_target — True als dit node het directe doel van een assignment is
                          (dan telt het NIET als "gelezen")

        Logica:
          - VariableNode in expressie-context → voeg naam toe aan used
          - VariableNode als directe target van AssignNode → NIET toevoegen
          - ArrayAccessNode als target → de array-naam NIET toevoegen,
            maar de index-expressie WEL evalueren (die wordt gelezen)
          - Alle andere nodes → recursief afdalen in kinderen

        EDGE CASE: int x = foo(); waarbij x nooit gelezen wordt →
          x is ongebruikt, maar foo() heeft side effects. visitVarDecl
          evalueert de RHS nog steeds; alleen de alloca/store worden overgeslagen.
        EDGE CASE: shadowing — we werken met namen, niet met LLVM-namen.
          Twee variabelen met dezelfde naam in verschillende scopes tellen allebei.
        """
        from ..parser.ast_nodes import (
            VariableNode, AssignNode, BinaryOpNode, UnaryOpNode,
            ArrayAccessNode, FunctionCallNode, ReturnNode, VarDeclNode,
            ArrayDeclNode, IfNode, WhileNode, BlockNode, ScopeNode,
            CastNode, LiteralNode, StringLiteralNode, CommentNode,
        )

        if node is None:
            return

        if isinstance(node, VariableNode):
            if not assign_target:
                used.add(node.name)
            return

        if isinstance(node, AssignNode):
            # target: alleen als array-access telt de array NIET mee,
            # maar de index WEL. Bij directe variabele: niet mee.
            if isinstance(node.target, ArrayAccessNode):
                self._collect_used_vars(node.target.index, used)
                # array-naam zelf is niet "gelezen" hier
            # EDGE CASE: *ptr = x → de pointer ptr wordt WEL gelezen
            # (we moeten hem laden om het adres te krijgen).
            elif isinstance(node.target, UnaryOpNode) and node.target.op == '*':
                self._collect_used_vars(node.target.operand, used)
            # in alle andere gevallen: target niet als gelezen markeren
            self._collect_used_vars(node.value, used)
            return

        if isinstance(node, VarDeclNode):
            # de naam die gedeclareerd wordt telt niet als lees
            if node.value is not None:
                self._collect_used_vars(node.value, used)
            return

        if isinstance(node, ArrayAccessNode):
            # array-naam: als we hier komen is het een lees-context
            if not assign_target:
                used.add(node.array_expr.name if isinstance(node.array_expr, VariableNode) else '')
            self._collect_used_vars(node.index, used)
            return

        # voor alle andere nodes: afdalen in alle kinderen
        for attr in ('left', 'right', 'operand', 'value', 'condition',
                     'then_block', 'else_block', 'body', 'update'):
            child = getattr(node, attr, None)
            if child is not None:
                self._collect_used_vars(child, used)

        # collecties (lijsten van nodes)
        for attr in ('statements', 'args', 'params', 'elements'):
            children = getattr(node, attr, None)
            if children:
                for child in children:
                    self._collect_used_vars(child, used)

    def visitVarDecl(self, node):
        """
        Genereer alloca + optioneel store voor een variabele declaratie.

        EDGE CASE: char* s = "hello" → alloca i8*, store i8* (GEP van global)
        EDGE CASE: impliciete type conversie bij initialisatie (float → int, enz.)
        """
        name     = node.name
        base     = node.var_type.base_type
        depth    = node.var_type.pointer_depth
        llvm_t   = self.llvm_type(base, depth)

        # unieke LLVM naam bij shadowing (x → x.1 als x al bestaat)
        llvm_name = self._get_unique_llvm_name(name)
        self.scope_stack[-1][name] = llvm_name  # registreer in huidige scope

        # sla type info op onder de unieke naam
        self.var_info[llvm_name] = {
            'base_type':     base,
            'pointer_depth': depth,
            'is_array':      False,
            'dimensions':    [],
            'llvm_type':     llvm_t
        }

        # ── Ongebruikte variabelen optimalisatie ────────────────────────────
        # Als de variabele nooit gelezen wordt, sla de alloca + store over.
        # De RHS-expressie wordt nog WEL geëvalueerd (side effects, bv. foo()).
        # UITZONDERING: globale variabelen altijd genereren (andere functies
        # kunnen ze lezen). Parameters worden niet via visitVarDecl aangemaakt.
        is_unused = (
            self._current_used_vars is not None
            and name not in self._current_used_vars
        )

        if is_unused:
            # Evalueer de RHS nog wel (side effects), maar gooi het resultaat weg
            if node.value is not None:
                node.value.accept(self)
            return

        # alloca met unieke naam
        self.emit(f"%{llvm_name} = alloca {llvm_t}")

        # store initialisatiewaarde als die er is
        if node.value is not None:
            val, val_type = node.value.accept(self)
            # EDGE CASE: int* ptr = 0  → 0 is een integer maar de variabele is een pointer.
            # In LLVM is 'null' de correcte nul-pointer, niet de integer 0.
            if depth > 0 and val == '0' and val_type in ('i32', 'i8'):
                val = 'null'
                val_type = llvm_t  # pointer type, geen coercering nodig
            else:
                val = self._coerce(val, val_type, llvm_t)
            self.emit(f"store {llvm_t} {val}, {llvm_t}* %{llvm_name}")

    def visitArrayDecl(self, node):
        """
        Genereer alloca + initialisatie voor een array declaratie.

        Voor int arr[3] = {1, 2, 3}:
          %arr = alloca [3 x i32]
          %t0 = getelementptr [3 x i32], [3 x i32]* %arr, i32 0, i32 0
          store i32 1, i32* %t0
          ... (voor elk element)

        EDGE CASE: lege initialisator → geen stores
        EDGE CASE: 2D array → geneste getelementptr met meerdere indices
        """
        name = node.name
        base = node.var_type.base_type
        dims = node.dimensions
        arr_t = self.llvm_array_type(base, dims)

        self.var_info[name] = {
            'base_type':    base,
            'pointer_depth': 0,
            'is_array':     True,
            'dimensions':   dims,
            'llvm_type':    arr_t
        }

        self.emit(f"%{name} = alloca {arr_t}")

        if node.initializer is not None:
            self._emit_array_init(name, arr_t, base, node.initializer, [])

    def _emit_array_init(self, array_name: str, array_t: str, base_type: str,
                         init_node, prefix_indices: list):
        """
        Emitteer store instructies voor een array initialisator.
        Recursief voor geneste initialisatoren (2D arrays).

        prefix_indices: de indices van de buitenste dimensies (voor 2D)
        """
        elem_t = self.llvm_base_type(base_type)

        for i, elem in enumerate(init_node.elements):
            current_indices = prefix_indices + [i]

            if isinstance(elem, ArrayInitNode):
                # geneste rij (2D) → recursief
                self._emit_array_init(array_name, array_t, base_type, elem, current_indices)
            else:
                # scalar waarde → getelementptr + store
                val, val_type = elem.accept(self)
                val = self._coerce(val, val_type, elem_t)

                # GEP: i32 0 (pointer deref) + indices per dimensie
                idx_str = 'i32 0, ' + ', '.join(f'i32 {idx}' for idx in current_indices)
                ptr_reg = self.new_reg()
                self.emit(f"{ptr_reg} = getelementptr {array_t}, {array_t}* %{array_name}, {idx_str}")
                self.emit(f"store {elem_t} {val}, {elem_t}* {ptr_reg}")

    def visitAssign(self, node):
        """
        Genereer code voor een assignment: target = value.

        Stap 1: evalueer de rechterkant → (val, type)
        Stap 2: bereken het adres van de linkerkant → (addr, ptr_type)
        Stap 3: coerceer val naar het doeltype
        Stap 4: store
        """
        val, val_type = node.value.accept(self)

        addr, addr_ptr_type = self._get_address(node.target)
        elem_type = addr_ptr_type[:-1]  # verwijder de trailing '*'

        val = self._coerce(val, val_type, elem_type)
        self.emit(f"store {elem_type} {val}, {addr_ptr_type} {addr}")

    # ============================================================
    # EXPRESSIES
    # ============================================================

    def visitLiteral(self, node) -> tuple:
        """
        Geeft de directe LLVM waarde terug voor een literal.
        Geen instructies nodig.

        EDGE CASE: char → geef ASCII waarde als i8
        EDGE CASE: float 16 (int opgeslagen als float na folding) → schrijf als 16.0
        """
        if node.type_name == 'int':
            return (str(node.value), 'i32')



        elif node.type_name == 'float':

            import struct

            v = float(node.value)

            # afronden naar single precision, dan uitdrukken als double hex

            single = struct.unpack('>f', struct.pack('>f', v))[0]

            packed = struct.pack('>d', single)

            hex_val = ''.join(f'{b:02X}' for b in packed)

            return (f"0x{hex_val}", 'float')

        elif node.type_name == 'char':
            if isinstance(node.value, str):
                return (str(ord(node.value)), 'i8')
            return (str(node.value), 'i8')
        return ('0', 'i32')

    def visitStringLiteral(self, node) -> tuple:
        """
        Maak/haal een globale string constante op en emitteer een GEP
        om een i8* pointer te krijgen.

        EDGE CASE: lege string "" → global is [1 x i8] c"\\00"
        """
        global_name = self.get_string_global(node.value)
        length  = self._string_byte_length(node.value) + 1
        arr_t   = f"[{length} x i8]"
        ptr_reg = self.new_reg()
        self.emit(f"{ptr_reg} = getelementptr {arr_t}, {arr_t}* {global_name}, i32 0, i32 0")
        return (ptr_reg, 'i8*')

    def visitVariable(self, node) -> tuple:
        """
        Emitteer een load instructie voor het lezen van een variabele.

        EDGE CASE: array variabele als expressie (bv. in sizeof of assignment)
        → dit is semantisch ongeldig, de semantic analysis heeft het al gemeld.
        We geven een nul terug als fallback.
        """
        llvm_name = self._lookup_llvm_name(node.name)
        info = self.var_info.get(llvm_name)
        if info is None:
            return ('0', 'i32')

        if info['is_array']:
            arr_t = self.llvm_array_type(info['base_type'], info['dimensions'])
            return (f"%{llvm_name}", f"{arr_t}*")

        llvm_t = self.llvm_type(info['base_type'], info['pointer_depth'])
        reg    = self.new_reg()
        prefix = '@' if info.get('is_global') else '%'
        self.emit(f"{reg} = load {llvm_t}, {llvm_t}* {prefix}{llvm_name}")
        return (reg, llvm_t)

    def visitArrayAccess(self, node) -> tuple:
        """
        Emitteer GEP + load voor arr[i] of arr[i][j].
        """
        addr, addr_ptr_type = self._get_array_element_address(node)
        elem_type = addr_ptr_type[:-1]
        reg = self.new_reg()
        self.emit(f"{reg} = load {elem_type}, {elem_type}* {addr}")
        return (reg, elem_type)

    def _ptr_elem_type(self, ptr_type: str) -> str:
        """Geeft het element-type terug van een pointer type: 'i32*' → 'i32'."""
        return ptr_type[:-1]

    def _ptr_elem_size(self, ptr_type: str) -> int:
        """
        Geeft de grootte in bytes van het element type van een pointer.
        Nodig voor ptr - ptr: het verschil in adressen delen door de elementgrootte.
          i8*    → 1
          i32*   → 4
          float* → 4
          i64*   → 8
        """
        sizes = {'i8': 1, 'i16': 2, 'i32': 4, 'i64': 8, 'float': 4, 'double': 8}
        return sizes.get(self._ptr_elem_type(ptr_type), 4)

    def _decay_array_ptr(self, val: str, val_type: str) -> tuple:
        """
        Array-to-pointer decay: zet een array pointer [N x T]* om naar T*.

        In C wordt een array naam automatisch omgezet naar een pointer naar
        het eerste element: int arr[5] → int* (punt naar arr[0]).

        Voorbeeld:
          val_type = '[5 x i32]*'
          → emit: %reg = getelementptr [5 x i32], [5 x i32]* %arr, i32 0, i32 0
          → return (%reg, 'i32*')

        Als val_type al een gewone pointer is (i32*, float*, ...) → ongewijzigd.
        EDGE CASE: [2 x [3 x i32]]* → decay naar [3 x i32]* (één laag afpellen).
        """
        import re
        m = re.match(r'^\[(\d+) x (.+)\]\*$', val_type)
        if m:
            n         = m.group(1)
            elem_type = m.group(2)
            arr_type  = f"[{n} x {elem_type}]"
            reg = self.new_reg()
            self.emit(f"{reg} = getelementptr {arr_type}, {arr_type}* {val}, i32 0, i32 0")
            return (reg, f"{elem_type}*")
        return (val, val_type)

    def _emit_pointer_op(self, op: str,
                         left_val: str,  left_type: str,
                         right_val: str, right_type: str) -> tuple:
        """
        Genereert LLVM IR voor pointer arithmetic en pointer vergelijkingen.

        Gevallen:
          ptr + int  →  getelementptr <elem>, <ptr_type> <ptr>, i32 <idx>
          int + ptr  →  zelfde (optelling is commutatief)
          ptr - int  →  getelementptr met -idx  (sub i32 0, idx)
          ptr - ptr  →  ptrtoint beide naar i64, sub, sdiv door elementgrootte, trunc naar i32
          ptr CMP x  →  ptrtoint ptr naar i64, x naar i64, icmp (unsigned voor ordening)

        EDGE CASE: ptr - int waarbij int een literal '5' is → we negeren het eerst via
          sub i32 0, 5 en geven dat als GEP-index mee.
        EDGE CASE: ptr == 0 of ptr != 0 (null-check) → 0 wordt omgezet naar i64 0 via sext.
        EDGE CASE: het element type van een pointer ptr_type = 'i32*' is 'i32'.
          Voor ptr - ptr: de afstand in bytes / 4 = afstand in elementen.
        """
        # ── Array-to-pointer decay ──────────────────────────────────────────
        # int arr[5] → [5 x i32]* in LLVM. Maar pointer arithmetic verwacht i32*.
        # Decay beide kanten vóór we verder gaan.
        left_val,  left_type  = self._decay_array_ptr(left_val,  left_type)
        right_val, right_type = self._decay_array_ptr(right_val, right_type)

        left_is_ptr  = left_type.endswith('*')
        right_is_ptr = right_type.endswith('*')

        # ── ptr + int  of  int + ptr ─────────────────────────────────────────
        if op == '+' and (left_is_ptr != right_is_ptr):
            if left_is_ptr:
                ptr_val, ptr_type = left_val, left_type
                idx_val, idx_type = right_val, right_type
            else:
                ptr_val, ptr_type = right_val, right_type
                idx_val, idx_type = left_val, left_type

            elem_type = self._ptr_elem_type(ptr_type)
            idx_val   = self._coerce(idx_val, idx_type, 'i32')
            reg = self.new_reg()
            self.emit(f"{reg} = getelementptr {elem_type}, {ptr_type} {ptr_val}, i32 {idx_val}")
            return (reg, ptr_type)

        # ── ptr - int ────────────────────────────────────────────────────────
        if op == '-' and left_is_ptr and not right_is_ptr:
            elem_type = self._ptr_elem_type(left_type)
            idx_val   = self._coerce(right_val, right_type, 'i32')
            neg_reg   = self.new_reg()
            self.emit(f"{neg_reg} = sub i32 0, {idx_val}")
            reg = self.new_reg()
            self.emit(f"{reg} = getelementptr {elem_type}, {left_type} {left_val}, i32 {neg_reg}")
            return (reg, left_type)

        # ── ptr - ptr ────────────────────────────────────────────────────────
        if op == '-' and left_is_ptr and right_is_ptr:
            size  = self._ptr_elem_size(left_type)
            l_int = self.new_reg()
            r_int = self.new_reg()
            diff  = self.new_reg()
            quot  = self.new_reg()
            result = self.new_reg()
            self.emit(f"{l_int} = ptrtoint {left_type} {left_val} to i64")
            self.emit(f"{r_int} = ptrtoint {right_type} {right_val} to i64")
            self.emit(f"{diff} = sub i64 {l_int}, {r_int}")
            self.emit(f"{quot} = sdiv i64 {diff}, {size}")
            self.emit(f"{result} = trunc i64 {quot} to i32")
            return (result, 'i32')

        # ── vergelijkingen met pointers ──────────────────────────────────────
        if op in ('==', '!=', '<', '>', '<=', '>='):
            if left_is_ptr:
                l64 = self.new_reg()
                self.emit(f"{l64} = ptrtoint {left_type} {left_val} to i64")
                cmp_left, cmp_left_t = l64, 'i64'
            else:
                cmp_left  = self._coerce(left_val, left_type, 'i64')
                cmp_left_t = 'i64'

            if right_is_ptr:
                r64 = self.new_reg()
                self.emit(f"{r64} = ptrtoint {right_type} {right_val} to i64")
                cmp_right, cmp_right_t = r64, 'i64'
            else:
                cmp_right  = self._coerce(right_val, right_type, 'i64')
                cmp_right_t = 'i64'

            # unsigned vergelijking voor pointer ordening (ult/ugt/ule/uge)
            # equality/inequality is signed-agnostic (eq/ne)
            cmp_map = {
                '==': 'eq',  '!=': 'ne',
                '<':  'ult', '>':  'ugt',
                '<=': 'ule', '>=': 'uge'
            }
            cmp_reg = self.new_reg()
            self.emit(f"{cmp_reg} = icmp {cmp_map[op]} i64 {cmp_left}, {cmp_right}")
            result = self.new_reg()
            self.emit(f"{result} = zext i1 {cmp_reg} to i32")
            return (result, 'i32')

        # fallback (bv. ptr * int heeft geen betekenis)
        return ('0', 'i32')

    def visitBinaryOp(self, node) -> tuple:
        """
        Emitteer een binaire operatie.

        Stap 1: evalueer beide operanden
        Stap 2: check op pointer arithmetic → delegeer naar _emit_pointer_op
        Stap 3: coerceer naar gemeenschappelijk type
        Stap 4: emitteer de juiste LLVM instructie

        LLVM instructies:
          int:   add, sub, mul, sdiv, srem, and, or, xor, shl, ashr
          float: fadd, fsub, fmul, fdiv
          cmp:   icmp (int), fcmp (float) → i1 → zext naar i32
          &&/||: icmp ne 0 op beide, dan and/or i1, zext
          ptr:   getelementptr, ptrtoint+sub+sdiv (zie _emit_pointer_op)
        """
        left_val,  left_type  = node.left.accept(self)
        right_val, right_type = node.right.accept(self)

        # ── POINTER ARITHMETIC — intercepteer vóór _common_type ─────────────
        # _common_type begrijpt geen pointer types → dit MOET eerst!
        left_is_ptr  = left_type.endswith('*')
        right_is_ptr = right_type.endswith('*')

        if left_is_ptr or right_is_ptr:
            return self._emit_pointer_op(
                node.op, left_val, left_type, right_val, right_type
            )

        result_type = self._common_type(left_type, right_type)
        left_val    = self._coerce(left_val,  left_type,  result_type)
        right_val   = self._coerce(right_val, right_type, result_type)

        reg = self.new_reg()
        is_float = (result_type == 'float')

        # ── vergelijkingsoperatoren ──────────────────────────────────────────
        if node.op in ('==', '!=', '<', '>', '<=', '>='):
            if is_float:
                cmp_map = {'==': 'oeq', '!=': 'one', '<': 'olt',
                           '>': 'ogt', '<=': 'ole', '>=': 'oge'}
                self.emit(f"{reg} = fcmp {cmp_map[node.op]} float {left_val}, {right_val}")
            else:
                cmp_map = {'==': 'eq', '!=': 'ne', '<': 'slt',
                           '>': 'sgt', '<=': 'sle', '>=': 'sge'}
                self.emit(f"{reg} = icmp {cmp_map[node.op]} {result_type} {left_val}, {right_val}")
            # zext i1 naar i32 voor gebruik in verdere berekeningen
            reg2 = self.new_reg()
            self.emit(f"{reg2} = zext i1 {reg} to i32")
            return (reg2, 'i32')

        # ── logische && en || ────────────────────────────────────────────────
        if node.op == '&&':
            l = self.new_reg()
            r = self.new_reg()
            a = self.new_reg()
            self.emit(f"{l} = icmp ne {result_type} {left_val}, 0")
            self.emit(f"{r} = icmp ne {result_type} {right_val}, 0")
            self.emit(f"{a} = and i1 {l}, {r}")
            self.emit(f"{reg} = zext i1 {a} to i32")
            return (reg, 'i32')

        if node.op == '||':
            l = self.new_reg()
            r = self.new_reg()
            o = self.new_reg()
            self.emit(f"{l} = icmp ne {result_type} {left_val}, 0")
            self.emit(f"{r} = icmp ne {result_type} {right_val}, 0")
            self.emit(f"{o} = or i1 {l}, {r}")
            self.emit(f"{reg} = zext i1 {o} to i32")
            return (reg, 'i32')

        # ── rekenkundige en bitwise operatoren ───────────────────────────────
        if is_float:
            float_ops = {'+': 'fadd', '-': 'fsub', '*': 'fmul', '/': 'fdiv'}
            op = float_ops.get(node.op)
            if op:
                self.emit(f"{reg} = {op} float {left_val}, {right_val}")
                return (reg, 'float')
        else:
            int_ops = {
                '+': 'add', '-': 'sub', '*': 'mul', '/': 'sdiv', '%': 'srem',
                '&': 'and', '|': 'or', '^': 'xor',
                '<<': 'shl', '>>': 'ashr'
            }
            op = int_ops.get(node.op)
            if op:
                self.emit(f"{reg} = {op} {result_type} {left_val}, {right_val}")
                return (reg, result_type)

        # onbekende operator (zou na semantic analysis niet mogen voorkomen)
        return ('0', 'i32')

    def visitUnaryOp(self, node) -> tuple:
        """
        Emitteer een unaire operatie.

        Speciale gevallen:
          &x        → geef het adres terug (geen load)
          *ptr      → load door de pointer
          prefix++  → load, add 1, store, geef NIEUWE waarde terug
          suffix++  → load, add 1, store, geef OUDE waarde terug
        """
        # ── address-of ──────────────────────────────────────────────────────
        if node.op == '&':
            addr, addr_type = self._get_address(node.operand)
            return (addr, addr_type)

        # ── pointer dereference ──────────────────────────────────────────────
        if node.op == '*':
            ptr_val, ptr_type = node.operand.accept(self)
            if not ptr_type.endswith('*'):
                return ('0', 'i32')  # type fout, zou niet mogen voorkomen
            elem_type = ptr_type[:-1]
            reg = self.new_reg()
            self.emit(f"{reg} = load {elem_type}, {ptr_type} {ptr_val}")
            return (reg, elem_type)

        # ── increment/decrement ──────────────────────────────────────────────
        if node.op in ('prefix++', 'prefix--', 'suffix++', 'suffix--'):
            addr, addr_ptr_type = self._get_address(node.operand)
            elem_type = addr_ptr_type[:-1]

            old_val = self.new_reg()
            new_val = self.new_reg()

            self.emit(f"{old_val} = load {elem_type}, {addr_ptr_type} {addr}")

            if elem_type.endswith('*'):
                # p++ of p-- op een pointer: GEP in plaats van add/sub
                inner_elem = self._ptr_elem_type(elem_type)
                delta      = '1' if '++' in node.op else '-1'
                self.emit(f"{new_val} = getelementptr {inner_elem}, {elem_type} {old_val}, i32 {delta}")
            else:
                llvm_op = 'add' if '++' in node.op else 'sub'
                self.emit(f"{new_val} = {llvm_op} {elem_type} {old_val}, 1")

            self.emit(f"store {elem_type} {new_val}, {addr_ptr_type} {addr}")

            # prefix geeft nieuwe waarde terug, suffix geeft oude waarde terug
            return (new_val if node.op.startswith('prefix') else old_val, elem_type)

        # ── gewone unaire operatoren ─────────────────────────────────────────
        operand_val, operand_type = node.operand.accept(self)
        reg = self.new_reg()

        if node.op == '-':
            if operand_type == 'float':
                self.emit(f"{reg} = fsub float 0.0, {operand_val}")
            else:
                self.emit(f"{reg} = sub {operand_type} 0, {operand_val}")
            return (reg, operand_type)

        elif node.op == '+':
            return (operand_val, operand_type)

        elif node.op == '!':
            cmp_reg = self.new_reg()
            self.emit(f"{cmp_reg} = icmp eq {operand_type} {operand_val}, 0")
            self.emit(f"{reg} = zext i1 {cmp_reg} to i32")
            return (reg, 'i32')

        elif node.op == '~':
            self.emit(f"{reg} = xor {operand_type} {operand_val}, -1")
            return (reg, operand_type)

        return ('0', 'i32')

    def visitCast(self, node) -> tuple:
        """
        Emitteer een expliciete type cast.

        LLVM instructies:
          float → int:  fptosi
          int → float:  sitofp
          int → char:   trunc (i32 → i8)
          char → int:   sext  (i8 → i32, sign-extend)
        """
        operand_val, operand_type = node.operand.accept(self)
        target_type = self.llvm_base_type(node.target_type.base_type)

        return (self._coerce(operand_val, operand_type, target_type), target_type)

    def visitFunctionCall(self, node) -> tuple:
        """
        Emitteer een functie-aanroep.

        printf/scanf: variadic calling convention  → call i32 (i8*, ...) @naam(...)
        user functies: vaste calling convention    → call <ret> @naam(...)

        Assignment 5: gebruik func_return_types voor het juiste return type.
        Argumenten worden gecoerceerd naar het verwachte parameter type.

        EDGE CASE: void functie → de aanroep geeft geen waarde terug.
          We geven ('0', 'i32') terug als fallback zodat de aanroep als
          expressie-statement gebruikt kan worden.
        EDGE CASE: char (i8) in variadic → sext naar i32 (C promotie-regels).
        EDGE CASE: float in variadic → fpext naar double.
        """
        # ── malloc: call i8* @malloc(i64 size) ────────────────────────────
        # malloc(n) geeft een i8* pointer naar heap-geheugen van n bytes.
        # De grootte wordt uitgebreid naar i64 (LLVM vereist dit).
        # De i8* wordt daarna gecast naar het gewenste pointer type door de
        # omringende CastNode of VarDeclNode.
        if node.name == 'malloc':
            self.func_decls.add('malloc')
            if node.args:
                size_val, size_type = node.args[0].accept(self)
                size_val = self._coerce(size_val, size_type, 'i64')
            else:
                size_val = '0'
            reg = self.new_reg()
            self.emit(f"{reg} = call i8* @malloc(i64 {size_val})")
            return (reg, 'i8*')

        # ── free: call void @free(i8* ptr) ─────────────────────────────────
        # free(ptr) geeft heap-geheugen terug.
        # De pointer wordt eerst gecast naar i8* (malloc geeft i8* terug).
        if node.name == 'free':
            self.func_decls.add('free')
            if node.args:
                ptr_val, ptr_type = node.args[0].accept(self)
                # cast naar i8* als het nog niet i8* is
                if ptr_type != 'i8*':
                    cast_reg = self.new_reg()
                    self.emit(f"{cast_reg} = bitcast {ptr_type} {ptr_val} to i8*")
                    ptr_val = cast_reg
            else:
                ptr_val = 'null'
            self.emit(f"call void @free(i8* {ptr_val})")
            return ('0', 'i32')

        is_variadic = node.name in ('printf', 'scanf')
        if is_variadic:
            self.func_decls.add(node.name)

        # evalueer argumenten
        arg_parts = []
        for arg in node.args:
            val, typ = arg.accept(self)
            if is_variadic:
                # variadic promotie
                if typ == 'i8':
                    promoted = self.new_reg()
                    self.emit(f"{promoted} = sext i8 {val} to i32")
                    val, typ = promoted, 'i32'
                elif typ == 'float':
                    promoted = self.new_reg()
                    self.emit(f"{promoted} = fpext float {val} to double")
                    val, typ = promoted, 'double'
            arg_parts.append(f"{typ} {val}")

        arg_str = ', '.join(arg_parts)
        llvm_ret = self.func_return_types.get(node.name, 'i32')

        if llvm_ret == 'void':
            # void functie → call zonder resultaatregister
            if is_variadic:
                self.emit(f"call void (i8*, ...) @{node.name}({arg_str})")
            else:
                self.emit(f"call void @{node.name}({arg_str})")
            return ('0', 'i32')   # geen return waarde
        else:
            reg = self.new_reg()
            if is_variadic:
                self.emit(f"{reg} = call i32 (i8*, ...) @{node.name}({arg_str})")
            else:
                self.emit(f"{reg} = call {llvm_ret} @{node.name}({arg_str})")
            return (reg, llvm_ret)

    def visitType(self, node):
        # TypeNode bevat geen code → niets te genereren
        return None

    def new_label(self, prefix: str) -> str:
        """
        Genereert een uniek LLVM label: prefix.N

        Elke aanroep verhoogt de globale teller, ook voor dezelfde prefix.
        Zo zijn labels nooit gelijk, ook niet bij geneste if/while.

        Voorbeelden:
          new_label("if.then")    → "if.then.0"
          new_label("while.cond") → "while.cond.1"
          new_label("if.then")    → "if.then.2"
        """
        lbl = f"{prefix}.{self.label_counter}"
        self.label_counter += 1
        return lbl

    def emit_label(self, name: str):
        """
        Emitteer een LLVM label-definitie (zonder inspringing).
        Reset _block_terminated zodat we daarna weer instructies kunnen emitteren.

          while.cond.0:
        """
        self.instructions.append(f"{name}:")
        self._block_terminated = False

    def emit_br(self, target: str):
        """
        Onvoorwaardelijke sprong: br label %target

        EDGE CASE: als het blok al afgesloten is (na break/continue/een
        eerdere br), emitteren we NIETS — anders twee terminators in één blok.
        """
        if not self._block_terminated:
            self.emit(f"br label %{target}")
            self._block_terminated = True

    def emit_cond_br(self, cond_reg: str, true_lbl: str, false_lbl: str):
        """
        Voorwaardelijke sprong: br i1 %cond, label %true, label %false

        Zelfde dead-code bescherming als emit_br.
        """
        if not self._block_terminated:
            self.emit(f"br i1 {cond_reg}, label %{true_lbl}, label %{false_lbl}")
            self._block_terminated = True

    def _to_bool(self, val: str, val_type: str) -> str:
        """
        Zet een LLVM waarde om naar i1 voor gebruik in 'br i1 ...'.

        In C is elke niet-nul waarde 'true':
          int/i8 → icmp ne <type> val, 0
          float  → fcmp one float val, 0.0   (ordered not-equal)
        """
        reg = self.new_reg()
        if val_type == 'float':
            self.emit(f"{reg} = fcmp one float {val}, 0.0")
        else:
            self.emit(f"{reg} = icmp ne {val_type} {val}, 0")
        return reg

    def visitProgram(self, node) -> str:
        """
        Assignment 5: itereer over globals in volgorde.

        Pass 1: registreer return types van alle functies zodat
                FunctionCall het juiste LLVM type kent.
        Pass 2: genereer LLVM IR per global item.
        """
        # Pass 1: return types registreren (voor correcte call-instructies)
        for item in node.globals:
            if isinstance(item, (FunctionDefNode, FunctionDeclNode)):
                ret_base  = item.return_type.base_type
                ret_depth = item.return_type.pointer_depth
                llvm_ret  = self.llvm_type(ret_base, ret_depth) if ret_base != 'void' else 'void'
                self.func_return_types[item.name] = llvm_ret

        # Pass 2: code genereren
        for item in node.globals:
            if isinstance(item, IncludeNode):
                item.accept(self)
            elif isinstance(item, VarDeclNode):
                base   = item.var_type.base_type
                depth  = item.var_type.pointer_depth
                llvm_t = self.llvm_type(base, depth)
                if item.value is not None and hasattr(item.value, 'value'):
                    init_val = item.value.value
                    if base == 'float':
                        import struct
                        single = struct.unpack('>f', struct.pack('>f', float(init_val)))[0]
                        packed = struct.pack('>d', single)
                        hex_val = ''.join(f'{b:02X}' for b in packed)
                        init_str = f"0x{hex_val}"
                    elif base == 'char' and isinstance(init_val, str):
                        init_str = str(ord(init_val))
                    else:
                        init_str = str(init_val)
                else:
                    init_str = '0' if base != 'float' else '0.0'
                self.globals.append(f'@{item.name} = global {llvm_t} {init_str}')
                self.global_var_info[item.name] = {
                    'base_type': base, 'pointer_depth': depth,
                    'is_array': False, 'dimensions': [],
                    'llvm_type': llvm_t, 'is_global': True,
                }
            elif isinstance(item, FunctionDefNode):
                item.accept(self)
            elif isinstance(item, FunctionDeclNode):
                item.accept(self)

        return self.finalize()

    # ── Assignment 5: FUNCTIE DEFINITIE ───────────────────────────────────────

    def visitFunctionDef(self, node: FunctionDefNode):
        """
        Genereer een volledige LLVM functiedefinitie.

        STRATEGIE: we slaan de huidige per-functie-state op, resetten alles
        voor de nieuwe functie, genereren de body, en bewaren het resultaat
        in self.functions.

        LLVM structuur:
          define <ret> @naam(<params>) {
          entry:
            ; alloca + store voor elke parameter
            ; body statements
            ; impliciete ret als void en body geen ret heeft
          }

        PARAMETERS: elke parameter krijgt een alloca + store. Dit is de
        standaard clang-aanpak: parameters zijn SSA waarden, maar we maken
        een stack slot zodat we ze kunnen lezen via load (ongewijzigd patroon).

        EDGE CASE: void functie zonder return → voeg 'ret void' toe.
        EDGE CASE: main() → geef altijd 'ret i32 0' als fallback.
        EDGE CASE: alle registers zijn globaal genummerd (reg_counter niet resetten)
          zodat labels nooit botsen tussen functies.
        """
        # ── sla huidige state op ──────────────────────────────────────────────
        saved_instructions      = self.instructions
        saved_var_info          = self.var_info
        saved_scope_stack       = self.scope_stack
        saved_name_counter      = self.name_counter
        saved_block_terminated  = self._block_terminated
        saved_func_name         = self.current_func_name
        saved_used_vars         = self._current_used_vars

        # ── reset voor deze functie ───────────────────────────────────────────
        self.instructions     = []
        self.var_info         = {}
        self.scope_stack      = [{}]
        self.name_counter     = {}
        self._block_terminated = False
        self.current_func_name = node.name

        # Bereken welke variabelen gelezen worden in deze functie.
        used = set()
        self._collect_used_vars(node.body, used)
        self._current_used_vars = used

        # Globale variabelen beschikbaar maken binnen deze functie
        for gname, ginfo in self.global_var_info.items():
            self.var_info[gname] = ginfo

        # ── LLVM parameter string opbouwen ────────────────────────────────────
        llvm_ret = self.func_return_types.get(node.name, 'i32')
        param_parts = []
        for param in node.params:
            p_llvm_t = self.llvm_type(param.param_type.base_type,
                                       param.param_type.pointer_depth)
            param_parts.append(f"{p_llvm_t} %{param.name}_arg")
        params_str = ', '.join(param_parts)

        # ── alloca + store voor elke parameter ────────────────────────────────
        # Parameters komen binnen als SSA waarden (%naam_arg).
        # We maken een stack slot (%naam) zodat de rest van de code
        # gewoon load/store kan gebruiken, net als bij lokale variabelen.
        for param in node.params:
            p_base  = param.param_type.base_type
            p_depth = param.param_type.pointer_depth
            p_llvm_t = self.llvm_type(p_base, p_depth)

            self.var_info[param.name] = {
                'base_type':     p_base,
                'pointer_depth': p_depth,
                'is_array':      False,
                'dimensions':    [],
                'llvm_type':     p_llvm_t,
            }
            self.scope_stack[-1][param.name] = param.name
            self.emit(f"%{param.name} = alloca {p_llvm_t}")
            self.emit(f"store {p_llvm_t} %{param.name}_arg, {p_llvm_t}* %{param.name}")

        # ── body ──────────────────────────────────────────────────────────────
        node.body.accept(self)

        # ── impliciete return als de body niet afsluit ────────────────────────
        if not self._block_terminated:
            if llvm_ret == 'void':
                self.emit('ret void')
            else:
                # fallback — semantic analysis zou dit al als warning gemeld hebben
                self.emit(f'ret {llvm_ret} 0')

        # ── bewaar de functie ──────────────────────────────────────────────────
        func_lines = [f'define {llvm_ret} @{node.name}({params_str}) {{',
                      'entry:']
        func_lines.extend(self.instructions)
        func_lines.append('}')
        self.functions.append(func_lines)

        # ── herstel state ──────────────────────────────────────────────────────
        self.instructions      = saved_instructions
        self.var_info          = saved_var_info
        self.scope_stack       = saved_scope_stack
        self.name_counter      = saved_name_counter
        self._block_terminated  = saved_block_terminated
        self.current_func_name  = saved_func_name
        self._current_used_vars = saved_used_vars

    def visitFunctionDecl(self, node: FunctionDeclNode):
        """
        Forward declarations genereren een LLVM 'declare' regel.
        Alleen nodig als de definitie in een ander compilatie-eenheid zit
        (bij ons: in een header). In ons geval hebben we de definitie altijd
        in hetzelfde bestand, dus dit is mostly a no-op.

        We sla de declaratie op als een speciale string in func_decls zodat
        finalize() hem kan uitsturen als de definitie er niet bij is.
        """
        # Als er al een definitie is (geregistreerd via visitFunctionDef),
        # dan hoeven we geen aparte declare te genereren.
        # We doen niets — de definitie zelf is voldoende.
        pass

    def visitReturn(self, node: ReturnNode):
        """
        Genereer een LLVM 'ret' instructie.

        LLVM vereist dat elke basic block eindigt met een terminator.
        'ret' is een terminator → _block_terminated = True via emit_br wordt
        hier handmatig gezet.

        EDGE CASE: ret void → 'ret void'
        EDGE CASE: ret met waarde → evalueer expressie, dan 'ret <type> <val>'
        EDGE CASE: return na return (dead code) → _block_terminated blokkeert
          dit al in visitBlock.
        """
        llvm_ret = self.func_return_types.get(self.current_func_name, 'i32')

        if node.value is None or llvm_ret == 'void':
            self.emit('ret void' if llvm_ret == 'void' else 'ret i32 0')
        else:
            val, val_type = node.value.accept(self)
            # EDGE CASE: pointer teruggeven als int (bv. return &x in int functie)
            # _coerce kent geen pointer→int conversie, dus we doen dat hier apart.
            if val_type.endswith('*') and llvm_ret in ('i32', 'i8'):
                reg = self.new_reg()
                self.emit(f"{reg} = ptrtoint {val_type} {val} to {llvm_ret}")
                val = reg
            else:
                val = self._coerce(val, val_type, llvm_ret)
            self.emit(f'ret {llvm_ret} {val}')

        self._block_terminated = True

    def visitDefine(self, node):
        pass  # preprocessor heeft al gedaan

    def visitIncludeFile(self, node):
        pass  # preprocessor heeft al gedaan

    def visitParam(self, node):
        pass  # parameters worden verwerkt in visitFunctionDef

    def visitBlock(self, node):
        """
        UITGEBREID: stopt zodra het blok afgesloten is (dead code na break/continue).
        Voegt na de EERSTE LLVM-instructie van elk statement een comment toe
        met de originele C-code, conform de assignment 3 eis.

        EDGE CASE: CommentNode genereert zelf al een comment via visitComment —
          die krijgt dus geen extra comment.
        EDGE CASE: als een statement nul instructies genereert (bv. EnumDefNode),
          wordt er geen comment toegevoegd.
        EDGE CASE: als de eerste nieuwe instructie al een label-definitie is
          (bv. 'if.then.0:'), plakken we het comment op de instructie DAARNA,
          want label-regels mogen geen inline comment hebben in LLVM IR.
        """
        from ..parser.ast_nodes import CommentNode

        for stmt in node.statements:
            if self._block_terminated:
                break

            # Houd bij hoeveel instructies er al zijn vóór dit statement
            idx_before = len(self.instructions)

            stmt.accept(self)

            # Geen comment voor CommentNode (heeft al een eigen LLVM comment)
            if isinstance(stmt, CommentNode):
                continue

            # Zoek de eerste nieuwe instructie die geen label is
            c_code = self._stmt_to_c(stmt)
            if not c_code:
                continue

            for i in range(idx_before, len(self.instructions)):
                instr = self.instructions[i].rstrip()
                # Label-regels eindigen op ':' zonder leading whitespace
                if instr.endswith(':') and not instr.startswith('  '):
                    continue  # label overslaan, zoek volgende instructie
                # Voeg comment toe aan het einde van deze instructie
                self.instructions[i] = f'{instr}  ; {c_code}'
                break  # alleen de EERSTE instructie krijgt het comment

    def visitEnumDef(self, node):
        """
        Enum definities genereren geen LLVM code.

        Alle enum labels zijn door constant folding al omgezet naar
        LiteralNode(0), LiteralNode(1), enz. in alle expressies.
        """
        pass

    def visitScope(self, node):
        """
        Anonieme scope: bezoek gewoon de body.

        Scoping is een compile-time concept — LLVM IR kent geen scopes.
        Variabelen krijgen gewoon een alloca in de main body, net als alle
        andere variabelen. Naamconflicten zijn al afgehandeld door de
        semantic analysis.
        """
        node.body.accept(self)

    def visitIf(self, node):
        """
        Genereer LLVM IR voor if / if-else / else-if.

        STRUCTUUR zonder else:
          %cond = icmp ne i32 %val, 0
          br i1 %cond, label %if.then.0, label %if.end.1
        if.then.0:
          ; body
          br label %if.end.1
        if.end.1:

        STRUCTUUR met else:
          br i1 %cond, label %if.then.0, label %if.else.2
        if.then.0:
          ; then body
          br label %if.end.1
        if.else.2:
          ; else body  (of geneste IfNode voor else-if)
          br label %if.end.1
        if.end.1:

        EDGE CASE: else_block kan een IfNode zijn → visitIf wordt recursief
          aangeroepen, labels blijven uniek dankzij de globale label_counter.
        EDGE CASE: break/continue in een tak zet _block_terminated=True →
          emit_br(end_label) emitteert de sprong dan NIET (geen dubbele terminator).
        EDGE CASE: lege body → visitBlock doet niets, emit_br sluit af.
        """
        # evalueer conditie
        cond_val, cond_type = node.condition.accept(self)
        cond_reg = self._to_bool(cond_val, cond_type)

        then_lbl = self.new_label("if.then")
        end_lbl = self.new_label("if.end")

        if node.else_block is not None:
            else_lbl = self.new_label("if.else")
            self.emit_cond_br(cond_reg, then_lbl, else_lbl)
        else:
            self.emit_cond_br(cond_reg, then_lbl, end_lbl)

        # then-tak
        self.emit_label(then_lbl)
        node.then_block.accept(self)
        self.emit_br(end_lbl)

        # else-tak
        if node.else_block is not None:
            self.emit_label(else_lbl)
            node.else_block.accept(self)  # BlockNode of IfNode
            self.emit_br(end_lbl)

        self.emit_label(end_lbl)

    def visitWhile(self, node):
        """
        Genereer LLVM IR voor while (en for→while vertaling).

        STRUCTUUR gewone while:
          br label %while.cond.0
        while.cond.0:
          %cond = icmp ne i32 %val, 0
          br i1 %cond, label %while.body.1, label %while.end.2
        while.body.1:
          ; body
          br label %while.cond.0
        while.end.2:

        STRUCTUUR for-lus (node.update aanwezig):
          br label %while.cond.0
        while.cond.0:
          br i1 %cond, label %while.body.1, label %while.end.2
        while.body.1:
          ; body statements (ZONDER de update — die staat in node.update)
          br label %while.update.3
        while.update.3:
          ; update expressie (bv. i + 1, i++)
          br label %while.cond.0
        while.end.2:

        LOOP STACK: (end_label, continue_target)
          - break    → spring naar end_label
          - continue → spring naar continue_target
                       = while.cond  voor gewone while
                       = while.update voor for-lus

        EDGE CASE: break/continue in geneste loops → loop_stack[-1] is de
          binnenste lus, break/continue horen altijd bij de binnenste.
        EDGE CASE: dead code na break in body → _block_terminated=True,
          emit_br(update/cond) wordt overgeslagen door emit_br check.
        EDGE CASE: while(1) → cond is LiteralNode(1) → icmp ne i32 1, 0
          → altijd true → oneindige lus (verwacht, geldig).
        """
        cond_lbl = self.new_label("while.cond")
        body_lbl = self.new_label("while.body")
        end_lbl = self.new_label("while.end")

        if node.update is not None:
            upd_lbl = self.new_label("while.update")
            continue_target = upd_lbl
        else:
            upd_lbl = None
            continue_target = cond_lbl

        # sluit het huidige blok af en spring naar conditie
        self.emit_br(cond_lbl)

        # ── conditie ──────────────────────────────────────────────
        self.emit_label(cond_lbl)
        cond_val, cond_type = node.condition.accept(self)
        cond_reg = self._to_bool(cond_val, cond_type)
        self.emit_cond_br(cond_reg, body_lbl, end_lbl)

        # ── body ──────────────────────────────────────────────────
        self.emit_label(body_lbl)
        self.loop_stack.append((end_lbl, continue_target))

        if node.update is not None:
            # de update staat als laatste statement in node.body (toegevoegd
            # door de CST→AST visitor). We emitteren de body ZONDER dat
            # laatste statement, zodat continue via het update-label loopt.
            for stmt in node.body.statements[:-1]:
                if self._block_terminated:
                    break
                stmt.accept(self)
        else:
            node.body.accept(self)

        self.loop_stack.pop()

        # ── update (alleen voor for-lussen) ───────────────────────
        if node.update is not None:
            self.emit_br(upd_lbl)
            self.emit_label(upd_lbl)
            node.update.accept(self)  # resultaat wordt weggegooid

        # terug naar conditie
        self.emit_br(cond_lbl)

        # ── exit ──────────────────────────────────────────────────
        self.emit_label(end_lbl)

    def visitContinue(self, node):
        """
        Genereer een sprong naar het continue-target van de dichtstbijzijnde lus.

        - Gewone while: spring naar while.cond
        - For-lus:      spring naar while.update (voer update uit vóór conditie)

        Leest loop_stack[-1][1] (= continue_label).
        """
        if self.loop_stack:
            _, cont_lbl = self.loop_stack[-1]
            self.emit_br(cont_lbl)

    def visitBreak(self, node):
        """
        Genereer een sprong naar het exit-label van de dichtstbijzijnde lus/switch.

        Leest loop_stack[-1][0] (= break_label).
        emit_br beschermt tegen dubbele terminators.
        """
        if self.loop_stack:
            break_lbl, _ = self.loop_stack[-1]
            self.emit_br(break_lbl)