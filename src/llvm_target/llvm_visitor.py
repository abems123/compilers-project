# src/llvm_target/llvm_visitor.py

from ..parser.ast_nodes import (
    LiteralNode, BinaryOpNode, UnaryOpNode,
    VariableNode, VarDeclNode, AssignNode,
    CastNode, TypeNode, BlockNode, ProgramNode,
    CommentNode, ArrayDeclNode, ArrayInitNode,
    ArrayAccessNode, StringLiteralNode,
    FunctionCallNode, IncludeNode,
    # NIEUW — assignment 4:
    EnumDefNode, IfNode, WhileNode, BreakNode, ContinueNode, ScopeNode
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
        self.instructions       = []        # instructies in de main body
        self.reg_counter        = 0         # teller voor %t0, %t1, ...
        self.str_counter        = 0         # teller voor @.str.0, @.str.1, ...
        self.string_cache       = {}        # raw_value → global_name (geen duplicaten)
        self.var_info           = {}        # naam → dict met type info
        self.stdio_included     = False
        self.label_counter      = 0    # unieke teller voor if/while labels
        self.loop_stack         = []   # stack van (break_label, continue_label)
        self._block_terminated  = False  # True na br/ret → geen dubbele terminator
        self.scope_stack        = [{}]   # stack van {original_name: llvm_name} per scope
        self.name_counter       = {}     # original_name → aantal keer gedeclareerd (voor unieke namen)

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
        """Assembleer de volledige LLVM IR output en geef als string terug."""
        lines = []

        # globale string constanten
        for g in self.globals:
            lines.append(g)
        if self.globals:
            lines.append('')

        # functie declaraties
        if 'printf' in self.func_decls:
            lines.append('declare i32 @printf(i8*, ...)')
        if 'scanf' in self.func_decls:
            lines.append('declare i32 @scanf(i8*, ...)')
        if self.func_decls:
            lines.append('')

        # main functie
        lines.append('define i32 @main() {')
        lines.append('entry:')
        lines.extend(self.instructions)
        lines.append('  ret i32 0')
        lines.append('}')

        return '\n'.join(lines)

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
            if info['is_array']:
                array_t = self.llvm_array_type(info['base_type'], info['dimensions'])
                return (f"%{llvm_name}", f"{array_t}*")
            else:
                llvm_t = self.llvm_type(info['base_type'], info['pointer_depth'])
                return (f"%{llvm_name}", f"{llvm_t}*")

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

        name   = current.name
        info   = self.var_info[name]
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

    def visitProgram(self, node) -> str:
        # verwerk includes (zet stdio_included vlag)
        for inc in node.includes:
            inc.accept(self)

        # genereer de body
        node.body.accept(self)

        return self.finalize()

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

        # alloca met unieke naam
        self.emit(f"%{llvm_name} = alloca {llvm_t}")

        # store initialisatiewaarde als die er is
        if node.value is not None:
            val, val_type = node.value.accept(self)
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
            return ('0', 'i32')  # zou na semantic analysis niet mogen voorkomen

        if info['is_array']:
            # array als expressie → geef de pointer terug (bv. voor &arr)
            arr_t = self.llvm_array_type(info['base_type'], info['dimensions'])
            return (f"%{llvm_name}", f"{arr_t}*")

        llvm_t = self.llvm_type(info['base_type'], info['pointer_depth'])
        reg    = self.new_reg()
        self.emit(f"{reg} = load {llvm_t}, {llvm_t}* %{llvm_name}")
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

    def visitBinaryOp(self, node) -> tuple:
        """
        Emitteer een binaire operatie.

        Stap 1: evalueer beide operanden
        Stap 2: coerceer naar gemeenschappelijk type
        Stap 3: emitteer de juiste LLVM instructie

        LLVM instructies:
          int:   add, sub, mul, sdiv, srem, and, or, xor, shl, ashr
          float: fadd, fsub, fmul, fdiv
          cmp:   icmp (int), fcmp (float) → i1 → zext naar i32
          &&/||: icmp ne 0 op beide, dan and/or i1, zext
        """
        left_val,  left_type  = node.left.accept(self)
        right_val, right_type = node.right.accept(self)

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
        Emitteer een printf of scanf aanroep.

        printf/scanf gebruiken variadic argumenten in LLVM:
          call i32 (i8*, ...) @printf(i8* %str, i32 %x, ...)

        EDGE CASE: geen argumenten → lege argumentenlijst
        EDGE CASE: char argument → sext naar i32 voor variadic calling convention
        """
        if node.name in ('printf', 'scanf'):
            self.func_decls.add(node.name)

        # evalueer alle argumenten
        arg_parts = []
        for arg in node.args:
            val, typ = arg.accept(self)
            # variadic functies: char (i8) wordt gepromoveerd naar i32
            if typ == 'i8':
                promoted = self.new_reg()
                self.emit(f"{promoted} = sext i8 {val} to i32")
                val = promoted
                typ = 'i32'
            elif typ == 'float':
                promoted = self.new_reg()
                self.emit(f"{promoted} = fpext float {val} to double")
                val = promoted
                typ = 'double'
            arg_parts.append(f"{typ} {val}")

        arg_str = ', '.join(arg_parts)
        reg = self.new_reg()

        if node.name in ('printf', 'scanf'):
            self.emit(f"{reg} = call i32 (i8*, ...) @{node.name}({arg_str})")
        else:
            self.emit(f"{reg} = call i32 @{node.name}({arg_str})")

        return (reg, 'i32')

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
        UITGEBREID: verwerkt nu ook node.enums vóór de body.

        Enums hoeven geen LLVM code te genereren — de constant folding
        visitor heeft alle enum labels al omgezet naar LiteralNodes.
        """
        for inc in node.includes:
            inc.accept(self)

        for enum in node.enums:
            enum.accept(self)

        node.body.accept(self)

        return self.finalize()

    def visitBlock(self, node):
        """
        UITGEBREID: stopt zodra het blok afgesloten is (dead code na break/continue).

        EDGE CASE: break of continue midden in een blok zet _block_terminated=True.
        De rest van het blok is dan dead code en wordt overgeslagen.
        """
        for stmt in node.statements:
            if self._block_terminated:
                break
            stmt.accept(self)

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