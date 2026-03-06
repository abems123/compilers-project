# src/parser/semantic_analysis_visitor.py

from .ast_nodes import (
    LiteralNode, BinaryOpNode, UnaryOpNode,
    VariableNode, VarDeclNode, AssignNode,
    CastNode, TypeNode, BlockNode, ProgramNode,
    # Assignment 3:
    CommentNode, ArrayDeclNode, ArrayInitNode,
    ArrayAccessNode, StringLiteralNode,
    FunctionCallNode, IncludeNode,
    # Assignment 4:
    EnumDefNode, IfNode, WhileNode,
    BreakNode, ContinueNode, ScopeNode,
    # Assignment 5 (nieuw):
    ParamNode, FunctionDeclNode, FunctionDefNode,
    ReturnNode, DefineNode, IncludeFileNode,
)
from .symbol_table import SymbolTable, SymbolEntry, FunctionTable, FunctionEntry


# Type hiërarchie voor impliciete conversies (van arm naar rijk):
#   char < int < float
TYPE_RANK = {'char': 0, 'int': 1, 'float': 2}


def richer_type(a: str, b: str) -> str:
    """Geeft het rijkste van twee basistypes terug."""
    if TYPE_RANK.get(a, -1) >= TYPE_RANK.get(b, -1):
        return a
    return b


class SemanticAnalysisVisitor:
    """
    Loopt over de AST en controleert op semantische fouten en warnings.

    Assignment 5 voegt toe:
      - visitProgram      : iteratie over globals ipv vaste main-structuur
      - visitFunctionDef  : registreer functie, check body, return type
      - visitFunctionDecl : registreer forward declaration, check duplicaten
      - visitReturn       : check return type vs omringende functie
      - visitDefine       : no-op (preprocessor heeft al gedaan)
      - visitIncludeFile  : no-op (preprocessor heeft al gedaan)
      - visitFunctionCall : uitgebreid — check of functie bestaat + parameter types
      - get_type          : uitgebreid — FunctionCallNode geeft juiste return type

    FUNCTIE TRACKING:
      - self.function_table    : FunctionTable — alle gedeclareerde/gedefinieerde functies
      - self.current_function  : FunctionEntry | None — de functie die we nu bezoeken
        Gebruikt door visitReturn om het verwachte return type te weten.

    SCOPE STRATEGIE (ongewijzigd):
      - Globale scope: geopend in visitProgram
      - Per functie: nieuwe scope in visitFunctionDef
      - Parameters worden in de functie-scope geregistreerd
      - if/while/scope: eigen scope via push/pop (ongewijzigd)
    """

    def __init__(self):
        self.symbol_table     = SymbolTable()
        self.function_table   = FunctionTable()   # NIEUW
        self.errors           = []
        self.warnings         = []
        self.included_headers = set()

        # Assignment 4:
        self.loop_depth   = 0
        self.switch_depth = 0
        self.enum_types   = {}

        # Assignment 5 nieuw:
        self.current_function: FunctionEntry | None = None  # welke functie bezoeken we nu?
        self.current_global_index: int = 0  # index in globals van de functie die we nu bezoeken

    # --------------------------------------------------------
    # Fout- en waarschuwingsrapportage (ongewijzigd)
    # --------------------------------------------------------

    def error(self, msg: str, line: int = None):
        location = f"line {line}: " if line else ""
        self.errors.append(f"[ Error ] {location}{msg}")

    def warning(self, msg: str, line: int = None):
        location = f"line {line}: " if line else ""
        self.warnings.append(f"[ Warning ] {location}{msg}")

    def print_results(self):
        for w in self.warnings:
            print(w)
        for e in self.errors:
            print(e)
        if not self.errors and not self.warnings:
            print("Semantische analyse: geen fouten of warnings gevonden.")

    def has_errors(self):
        return len(self.errors) > 0

    # --------------------------------------------------------
    # Hulpmethode: bepaal het type van een expressie
    # --------------------------------------------------------

    def get_type(self, node) -> tuple:
        """
        Bepaalt het type van een expressie node.
        Geeft (base_type, pointer_depth) terug.

        NIEUW in assignment 4:
          - VariableNode die een enum label is → ('int', 0)
            Enum labels zijn const int in onze implementatie.
        """
        if isinstance(node, LiteralNode):
            return (node.type_name, 0)

        elif isinstance(node, StringLiteralNode):
            return ('char', 1)

        elif isinstance(node, VariableNode):
            entry = self.symbol_table.lookup(node.name)
            if entry is None:
                return ('unknown', 0)
            # enum labels zijn opgeslagen als base_type='int'
            return (entry.base_type, entry.pointer_depth)

        elif isinstance(node, ArrayAccessNode):
            base_name = self._get_array_base_name(node)
            if base_name is None:
                return ('unknown', 0)
            entry = self.symbol_table.lookup(base_name)
            if entry is None:
                return ('unknown', 0)
            return (entry.base_type, 0)

        elif isinstance(node, BinaryOpNode):
            left_type,  _ = self.get_type(node.left)
            right_type, _ = self.get_type(node.right)
            if node.op in ('==', '!=', '<', '>', '<=', '>=', '&&', '||'):
                return ('int', 0)
            return (richer_type(left_type, right_type), 0)

        elif isinstance(node, UnaryOpNode):
            if node.op == '&':
                base_type, depth = self.get_type(node.operand)
                return (base_type, depth + 1)
            elif node.op == '*':
                base_type, depth = self.get_type(node.operand)
                return (base_type, max(0, depth - 1))
            elif node.op in ('!',):
                return ('int', 0)
            else:
                return self.get_type(node.operand)

        elif isinstance(node, CastNode):
            return (node.target_type.base_type, node.target_type.pointer_depth)

        elif isinstance(node, FunctionCallNode):
            # Assignment 5: zoek het echte return type op in de function_table
            func_entry = self.function_table.lookup(node.name)
            if func_entry is not None:
                return func_entry.return_type
            return ('int', 0)  # fallback voor onbekende functies (bv. printf)

        return ('unknown', 0)

    def _get_array_base_name(self, node) -> str:
        """Navigeert naar de diepste VariableNode in een ArrayAccess keten."""
        if isinstance(node, VariableNode):
            return node.name
        elif isinstance(node, ArrayAccessNode):
            return self._get_array_base_name(node.array_expr)
        return None

    def is_lvalue(self, node) -> bool:
        if isinstance(node, VariableNode):
            return True
        if isinstance(node, UnaryOpNode) and node.op == '*':
            return True
        if isinstance(node, ArrayAccessNode):
            return True
        return False

    # --------------------------------------------------------
    # STRUCTUUR
    # --------------------------------------------------------

    def visitProgram(self, node):
        """
        Assignment 5: itereer over globals in volgorde.

        Twee passes:
          Pass 1 — registreer alle functies (decl + def) zodat forward
                   declarations altijd gevonden worden, ook al staan ze
                   na de aanroep (voor mutual recursion).
          Pass 2 — bezoek de bodies van alle functies + globale variabelen.

        Na afloop: check dat main() bestaat.
        """
        self.symbol_table.push_scope()

        # ── Pass 1: registreer alle functies ──────────────────────────────
        # Bijhouden op welke positie (index) elke functie voor het eerst
        # verschijnt, zodat we "aanroep vóór declaratie" kunnen detecteren.
        self.func_global_index = {}  # functienaam → index in globals

        for i, item in enumerate(node.globals):
            if isinstance(item, FunctionDeclNode):
                if item.name not in self.func_global_index:
                    self.func_global_index[item.name] = i
                self._register_func_decl(item)
            elif isinstance(item, FunctionDefNode):
                if item.name not in self.func_global_index:
                    self.func_global_index[item.name] = i
                self._register_func_def(item)
            elif isinstance(item, EnumDefNode):
                item.accept(self)
            elif isinstance(item, IncludeNode):
                item.accept(self)
            elif isinstance(item, IncludeFileNode):
                pass

        # ── Pass 2: bezoek bodies en globale variabelen ───────────────────
        for i, item in enumerate(node.globals):
            if isinstance(item, FunctionDefNode):
                self.current_global_index = i
                item.accept(self)
            elif isinstance(item, VarDeclNode):
                item.accept(self)

        # ── Check: main() moet aanwezig zijn ──────────────────────────────
        main_entry = self.function_table.lookup('main')
        if main_entry is None or not main_entry.is_defined:
            self.error("Functie 'main' ontbreekt. Elk C programma moet een main() hebben.")

        # ── Check: elke forward declaration moet een definitie hebben ──────
        for func in self.function_table.all_functions():
            if func.is_declared and not func.is_defined:
                self.error(
                    f"Forward declaration van '{func.name}' heeft geen bijbehorende definitie."
                )

        self.symbol_table.pop_scope()

    # --------------------------------------------------------
    # Hulpmethoden voor functie registratie
    # --------------------------------------------------------

    def _type_node_to_tuple(self, type_node: TypeNode) -> tuple:
        """Zet een TypeNode om naar een (base_type, pointer_depth) tuple."""
        return (type_node.base_type, type_node.pointer_depth)

    def _params_to_tuples(self, params: list) -> list:
        """Zet een lijst ParamNodes om naar [(base_type, pointer_depth), ...]"""
        return [self._type_node_to_tuple(p.param_type) for p in params]

    def _register_func_decl(self, node: FunctionDeclNode):
        """
        Registreer een forward declaration.

        EDGE CASE: al eerder gedeclareerd → check dat signatures overeenkomen.
        EDGE CASE: al eerder gedefinieerd → check dat signatures overeenkomen.
        EDGE CASE: definitie komt VÓÓR forward declaration in broncode →
          dit is een warning in C, bij ons een error.
        """
        ret   = self._type_node_to_tuple(node.return_type)
        params = self._params_to_tuples(node.params)

        existing = self.function_table.lookup(node.name)
        if existing is not None:
            # check consistentie
            self._check_signature_match(existing, ret, params, node.name, "declaratie")
            existing.is_declared = True
        else:
            entry = FunctionEntry(
                name        = node.name,
                return_type = ret,
                params      = params,
                is_defined  = False,
                is_declared = True,
            )
            self.function_table.declare(entry)

    def _register_func_def(self, node: FunctionDefNode):
        """
        Registreer een functiedefinitie (zonder de body te bezoeken).

        EDGE CASE: al eerder gedefinieerd → redefinitie error.
        EDGE CASE: al eerder gedeclareerd → check dat signatures overeenkomen.
        """
        ret    = self._type_node_to_tuple(node.return_type)
        params = self._params_to_tuples(node.params)

        existing = self.function_table.lookup(node.name)
        if existing is not None:
            if existing.is_defined:
                self.error(f"Herdefiniëring van functie '{node.name}'.")
                return
            # forward declaration aanwezig: check consistentie
            self._check_signature_match(existing, ret, params, node.name, "definitie")
            existing.is_defined  = True
            existing.return_type = ret
            existing.params      = params
        else:
            entry = FunctionEntry(
                name        = node.name,
                return_type = ret,
                params      = params,
                is_defined  = True,
                is_declared = False,
            )
            self.function_table.declare(entry)

    def _check_signature_match(self, existing: FunctionEntry,
                                ret: tuple, params: list,
                                name: str, context: str):
        """
        Check of een nieuwe declaratie/definitie overeenkomt met een
        bestaande forward declaration of definitie.
        """
        if existing.return_type != ret:
            self.error(
                f"Inconsistent return type voor '{name}' in {context}: "
                f"verwacht '{existing.return_type[0]}', gevonden '{ret[0]}'."
            )
        if len(existing.params) != len(params):
            self.error(
                f"Inconsistent aantal parameters voor '{name}' in {context}: "
                f"verwacht {len(existing.params)}, gevonden {len(params)}."
            )
        else:
            for i, (exp, got) in enumerate(zip(existing.params, params)):
                if exp != got:
                    self.error(
                        f"Parameter {i+1} van '{name}' in {context}: "
                        f"type mismatch — verwacht '{exp[0]}{'*'*exp[1]}', "
                        f"gevonden '{got[0]}{'*'*got[1]}'."
                    )

    # --------------------------------------------------------
    # Assignment 5: FUNCTIE DEFINITIE
    # --------------------------------------------------------

    def visitFunctionDef(self, node: FunctionDefNode):
        """
        Bezoek de body van een functiedefinitie.

        Stappen:
          1. Haal de FunctionEntry op uit de function_table (al geregistreerd)
          2. Sla current_function op zodat visitReturn het return type kent
          3. Open een nieuwe scope voor de functie
          4. Registreer parameters als lokale variabelen
          5. Bezoek de body
          6. Herstel current_function en pop_scope

        EDGE CASE: twee parameters met dezelfde naam → redeclaratie error.
        EDGE CASE: parameter heeft dezelfde naam als globale variabele →
          shadowing, de lokale parameter wint (geen error, wel geldige C).
        EDGE CASE: recursieve aanroep → de functie staat al in function_table
          (geregistreerd in pass 1), dus FunctionCallNode vindt hem.
        """
        entry = self.function_table.lookup(node.name)
        if entry is None:
            return  # zou niet mogen na pass 1

        prev_function = self.current_function
        self.current_function = entry

        self.symbol_table.push_scope()

        # registreer parameters als lokale variabelen
        for param in node.params:
            existing = self.symbol_table.lookup_current_scope(param.name)
            if existing is not None:
                self.error(
                    f"Parameter '{param.name}' van functie '{node.name}' "
                    f"is dubbel gedeclareerd."
                )
            else:
                sym = SymbolEntry(
                    name          = param.name,
                    base_type     = param.param_type.base_type,
                    pointer_depth = param.param_type.pointer_depth,
                    is_const      = param.param_type.is_const,
                    is_defined    = True,
                )
                self.symbol_table.declare(sym)

        # bezoek de body
        node.body.accept(self)

        self.symbol_table.pop_scope()
        self.current_function = prev_function

    def visitFunctionDecl(self, node: FunctionDeclNode):
        """Forward declarations zijn al verwerkt in pass 1 — no-op hier."""
        pass

    # --------------------------------------------------------
    # Assignment 5: RETURN STATEMENT
    # --------------------------------------------------------

    def visitReturn(self, node: ReturnNode):
        """
        Checks:
          1. Return buiten een functie → error
          2. Return met waarde in void functie → error
          3. Return zonder waarde in non-void functie → warning
          4. Return type mismatch → warning

        EDGE CASE: return; in void functie → geldig.
        EDGE CASE: return 0; in main() → geldig (int return type).
        EDGE CASE: return in geneste if/while → springt altijd uit de functie.
        """
        # check 1: buiten functie?
        if self.current_function is None:
            self.error("'return' gebruikt buiten een functie.")
            return

        ret_base, ret_depth = self.current_function.return_type

        if node.value is None:
            # return; — alleen geldig in void functies
            if ret_base != 'void':
                self.error(
                    f"Functie '{self.current_function.name}' heeft return type "
                    f"'{ret_base}' maar gebruikt 'return;' zonder waarde."
                )
        else:
            # return <expr>;
            node.value.accept(self)

            if ret_base == 'void':
                self.error(
                    f"Void functie '{self.current_function.name}' "
                    f"mag geen waarde teruggeven."
                )
            else:
                # type check
                val_base, val_depth = self.get_type(node.value)
                if val_base != 'unknown':
                    # pointer depth mismatch → altijd een error (int vs float* zijn onverenigbaar)
                    if val_depth != ret_depth:
                        self.error(
                            f"Return type mismatch in '{self.current_function.name}': "
                            f"functie verwacht '{ret_base}{'*'*ret_depth}', "
                            f"maar geeft '{val_base}{'*'*val_depth}' terug."
                        )
                    elif val_base in TYPE_RANK and ret_base in TYPE_RANK:
                        if TYPE_RANK[val_base] > TYPE_RANK[ret_base]:
                            self.warning(
                                f"Return type mismatch in '{self.current_function.name}': "
                                f"functie verwacht '{ret_base}', "
                                f"maar geeft '{val_base}' terug (mogelijk precisieverlies)."
                            )

    # --------------------------------------------------------
    # Assignment 5: DEFINE / INCLUDE FILE
    # --------------------------------------------------------

    def visitDefine(self, node: DefineNode):
        """Preprocessor heeft defines al verwerkt — no-op."""
        pass

    def visitIncludeFile(self, node: IncludeFileNode):
        """Preprocessor heeft includes al ingeladen — no-op."""
        pass

    def visitInclude(self, node):
        self.included_headers.add(node.header)

    def visitBlock(self, node):
        """
        Bezoek alle statements in een blok.
        GEEN push/pop scope hier — dat doen de callers (visitIf, visitWhile, enz.)
        zodat we geen dubbele scope krijgen.
        """
        for stmt in node.statements:
            stmt.accept(self)

    # --------------------------------------------------------
    # NIEUW: ENUM DEFINITIE
    # --------------------------------------------------------

    def visitEnumDef(self, node):
        """
        Registreer de enum en zijn labels in de symbol table.

        Stappen:
          1. Sla de enum op in self.enum_types (voor latere type checks)
          2. Registreer elk label als 'const int' in de huidige scope

        EDGE CASE: twee enums met hetzelfde label → tweede overschrijft
        de eerste in de symbol table. We geven een warning.

        EDGE CASE: een enum label heeft dezelfde naam als een bestaande
        variabele → we geven een error (redeclaratie).

        EDGE CASE: lege enum (geen labels) → enum_types registreren met
        lege lijst, geen labels toevoegen. Syntactisch al verboden door
        de grammar, maar voor de zekerheid.
        """
        # registreer de enum zelf
        if node.name in self.enum_types:
            self.warning(f"Enum '{node.name}' is al eerder gedefinieerd.")
        self.enum_types[node.name] = node.labels

        # registreer elk label als const int
        for i, label in enumerate(node.labels):
            existing = self.symbol_table.lookup_current_scope(label)
            if existing is not None:
                self.error(
                    f"Enum label '{label}' is al gedeclareerd als "
                    f"'{existing.type_str()}' in dezelfde scope."
                )
                continue

            entry = SymbolEntry(
                name          = label,
                base_type     = 'int',
                pointer_depth = 0,
                is_const      = True,   # enum labels zijn immutable
                is_defined    = True,
            )
            self.symbol_table.declare(entry)

    # --------------------------------------------------------
    # NIEUW: CONTROL FLOW
    # --------------------------------------------------------

    def visitIf(self, node):
        """
        Checks:
          - Verwerk de conditie
          - Open een nieuwe scope voor de then-tak
          - Open een nieuwe scope voor de else-tak (als aanwezig)

        GEEN type check op de conditie: in C is elke int/pointer
        geldig als conditie (0 = false, rest = true).

        EDGE CASE: else_block kan een IfNode zijn (else-if) —
        visitIf wordt dan recursief aangeroepen.
        """
        node.condition.accept(self)

        # then-tak: eigen scope
        self.symbol_table.push_scope()
        node.then_block.accept(self)
        self.symbol_table.pop_scope()

        # else-tak: eigen scope (ook als het een IfNode is)
        if node.else_block is not None:
            self.symbol_table.push_scope()
            node.else_block.accept(self)
            self.symbol_table.pop_scope()

    def visitWhile(self, node):
        """
        Checks:
          - Verwerk de conditie
          - Verhoog loop_depth zodat break/continue geldig zijn
          - Open een nieuwe scope voor de body
          - Verlaag loop_depth na de body

        EDGE CASE: WhileNode.update kan aanwezig zijn (for-lus vertaling).
        Die wordt ook bezocht voor variabele-gebruik checks.
        """
        node.condition.accept(self)

        self.loop_depth += 1
        self.symbol_table.push_scope()
        node.body.accept(self)
        self.symbol_table.pop_scope()
        self.loop_depth -= 1

        # update expressie (for-lus) — bezoek buiten de scope
        # (de update zit al IN de body, maar we bewaren hem ook apart
        #  in WhileNode.update voor de LLVM visitor; geen dubbele check nodig)

    def visitBreak(self, node):
        """
        Break is geldig binnen een lus (loop_depth > 0) OF
        binnen een switch (switch_depth > 0).

        EDGE CASE: break buiten beide → semantic error.
        """
        if self.loop_depth == 0 and self.switch_depth == 0:
            self.error(
                "'break' gebruikt buiten een lus of switch statement."
            )

    def visitContinue(self, node):
        """
        Continue is ALLEEN geldig binnen een lus (loop_depth > 0).
        Een continue binnen een switch (maar buiten een lus) is een error.

        EDGE CASE: continue in een switch die in een lus zit →
        loop_depth > 0, dus geldig.
        """
        if self.loop_depth == 0:
            self.error(
                "'continue' gebruikt buiten een lus. "
                "'continue' is niet geldig in een switch statement."
            )

    def visitScope(self, node):
        """
        Anonieme scope: push/pop een nieuwe scope om variabelen
        in te isoleren van de omringende code.

        EDGE CASE: variabele gedeclareerd in een anonieme scope en dan
        gebruikt buiten die scope → symbol_table.lookup() vindt hem niet
        meer na pop_scope() → error in visitVariable.
        """
        self.symbol_table.push_scope()
        node.body.accept(self)
        self.symbol_table.pop_scope()

    # --------------------------------------------------------
    # DECLARATIES EN ASSIGNMENTS
    # --------------------------------------------------------

    def visitVarDecl(self, node):
        """
        Checks:
          1. Redeclaratie in dezelfde scope
          2. NIEUW: als het type een enum is, check of de enum naam bekend is
          3. Als er een initialisatiewaarde is: bezoek die + type check
          4. Voeg toe aan symbol table

        EDGE CASE: enum Status x = READY;
          - node.var_type.base_type = 'Status'
          - 'Status' moet in self.enum_types staan
          - READY is een geldig enum label van Status
          We checken dit via de symbol table: READY is al als const int
          geregistreerd door visitEnumDef, dus visitVariable vindt het.

        EDGE CASE: enum variabele zonder initialisatie is geldig:
          enum Status x;  → is_defined = False
        """
        # check 1: redeclaratie
        existing = self.symbol_table.lookup_current_scope(node.name)
        if existing is not None:
            self.error(
                f"Herhaalde declaratie van variabele '{node.name}'. "
                f"Eerste declaratie was van type '{existing.type_str()}'."
            )
            return

        # check 2: enum type check
        base = node.var_type.base_type
        if base not in ('int', 'float', 'char') and node.var_type.pointer_depth == 0:
            # het is een enum type — check of de enum naam bekend is
            if base not in self.enum_types:
                self.error(
                    f"Onbekend type '{base}'. "
                    f"Is dit een enum die niet gedefinieerd is?"
                )

        # voeg toe aan symbol table
        entry = SymbolEntry(
            name          = node.name,
            base_type     = base if base in ('int', 'float', 'char') else 'int',
            pointer_depth = node.var_type.pointer_depth,
            is_const      = node.var_type.is_const,
            is_defined    = node.value is not None
        )
        self.symbol_table.declare(entry)

        # check 3: initialisatiewaarde bezoeken
        if node.value is not None:
            node.value.accept(self)
            self._check_implicit_conversion(
                target_type  = entry.base_type,
                target_depth = node.var_type.pointer_depth,
                value_node   = node.value,
                context      = f"declaratie van '{node.name}'"
            )

    def visitArrayDecl(self, node):
        """Ongewijzigd van assignment 3."""
        existing = self.symbol_table.lookup_current_scope(node.name)
        if existing is not None:
            self.error(
                f"Herhaalde declaratie van array '{node.name}'. "
                f"Eerste declaratie was van type '{existing.type_str()}'."
            )
            return

        entry = SymbolEntry(
            name          = node.name,
            base_type     = node.var_type.base_type,
            pointer_depth = node.var_type.pointer_depth,
            is_const      = node.var_type.is_const,
            is_defined    = node.initializer is not None,
            is_array      = True,
            dimensions    = node.dimensions
        )
        self.symbol_table.declare(entry)

        if node.initializer is not None:
            self._check_array_init(node.initializer, node.dimensions, node.name)

    def _check_array_init(self, init_node, dimensions, array_name):
        """Ongewijzigd van assignment 3."""
        if not dimensions:
            return

        expected_len = dimensions[0]
        actual_len   = len(init_node.elements)

        if actual_len != expected_len:
            self.error(
                f"Array '{array_name}': initialisator heeft {actual_len} element(en), "
                f"maar de dimensie is {expected_len}."
            )

        for elem in init_node.elements:
            if isinstance(elem, ArrayInitNode):
                if len(dimensions) > 1:
                    self._check_array_init(elem, dimensions[1:], array_name)
            else:
                elem.accept(self)

    def visitAssign(self, node):
        """
        Ongewijzigd van assignment 3, maar nu ook geldig voor anonieme scopes.

        NIEUW: check of de target geen enum label is (enum labels zijn const).
        EDGE CASE: READY = 5; → READY is const → error.
        """
        node.value.accept(self)

        if not self.is_lvalue(node.target):
            self.error(
                f"Linkerkant van assignment is geen geldig lvalue: {node.target}"
            )
            return

        # check const assignment
        if isinstance(node.target, VariableNode):
            entry = self.symbol_table.lookup(node.target.name)
            if entry is not None and entry.is_const:
                self.error(
                    f"Kan niet toewijzen aan const variabele '{node.target.name}'."
                )

        node.target.accept(self)

        target_type, target_depth = self.get_type(node.target)
        self._check_implicit_conversion(
            target_type  = target_type,
            target_depth = target_depth,
            value_node   = node.value,
            context      = f"assignment naar '{node.target}'"
        )

    def _check_implicit_conversion(self, target_type, target_depth, value_node, context):
        """Ongewijzigd van assignment 3."""
        value_type, value_depth = self.get_type(value_node)

        if value_type == 'unknown':
            return

        if target_depth != value_depth:
            if not (target_depth == 1 and value_depth == 0 and value_type == 'char'):
                self.warning(
                    f"Pointer diepte mismatch in {context}: "
                    f"verwacht {'*' * target_depth}{target_type}, "
                    f"gevonden {'*' * value_depth}{value_type}."
                )
            return

        if target_depth == 0 and value_depth == 0:
            if target_type in TYPE_RANK and value_type in TYPE_RANK:
                if TYPE_RANK[value_type] > TYPE_RANK[target_type]:
                    self.warning(
                        f"Mogelijke precisieverlies in {context}: "
                        f"{value_type} naar {target_type}."
                    )

    # --------------------------------------------------------
    # EXPRESSIES (ongewijzigd van assignment 3, behalve visitVariable)
    # --------------------------------------------------------

    def visitLiteral(self, node):
        pass

    def visitStringLiteral(self, node):
        pass

    def visitComment(self, node):
        pass

    def visitVariable(self, node):
        """
        Check: is de variabele gedeclareerd?

        NIEUW: enum labels zijn als const int geregistreerd door visitEnumDef,
        dus ze worden hier automatisch gevonden. Geen aparte enum-label check nodig.

        EDGE CASE: als de variabele niet gevonden wordt, geven we een error.
        """
        entry = self.symbol_table.lookup(node.name)
        if entry is None:
            self.error(
                f"Gebruik van niet-gedeclareerde variabele of enum label '{node.name}'."
            )

    def _visit_array_indices(self, node):
        """Ongewijzigd van assignment 3."""
        node.index.accept(self)
        if isinstance(node.array_expr, ArrayAccessNode):
            self._visit_array_indices(node.array_expr)

    def visitArrayAccess(self, node):
        """Ongewijzigd van assignment 3."""
        self._visit_array_indices(node)

        base_name = self._get_array_base_name(node.array_expr)
        if base_name is not None:
            entry = self.symbol_table.lookup(base_name)
            if entry is None:
                self.error(f"Gebruik van niet-gedeclareerde array '{base_name}'.")
            elif not entry.is_array:
                self.error(
                    f"Variabele '{base_name}' is geen array "
                    f"en kan niet geïndexeerd worden."
                )

        index_type, index_depth = self.get_type(node.index)
        if index_depth > 0:
            self.error(
                f"Array index mag geen pointer zijn. "
                f"Gevonden type: {'*' * index_depth}{index_type}."
            )
        elif index_type not in ('int', 'char', 'unknown'):
            self.warning(
                f"Array index is van type '{index_type}', verwacht 'int'."
            )

    def visitBinaryOp(self, node):
        node.left.accept(self)
        node.right.accept(self)

    def visitUnaryOp(self, node):
        if node.op == '&':
            if not self.is_lvalue(node.operand):
                self.error(
                    f"Adres-van operator '&' vereist een lvalue, "
                    f"maar gevonden: {node.operand}"
                )
        node.operand.accept(self)

    def visitCast(self, node):
        node.operand.accept(self)

    def visitType(self, node):
        pass

    def visitFunctionCall(self, node: FunctionCallNode):
        """
        Assignment 5: uitgebreid met volledige functie-checks.

        Checks:
          1. printf/scanf: stdio.h check (ongewijzigd)
          2. Overige functies: bestaat de functie?
          3. Correct aantal argumenten?
          4. Correct type per argument?

        EDGE CASE: printf/scanf hebben variabel aantal argumenten →
          we checken alleen dat stdio.h geïncludeerd is.
        EDGE CASE: functie aanroepen vóór declaratie → in pass 1 zijn alle
          functies al geregistreerd, dus dit werkt voor functies in hetzelfde
          bestand. Voor functies uit headers: ook opgelost door pass 1.
        EDGE CASE: recursieve aanroep → functie staat al in function_table.
        """
        # altijd de argumenten bezoeken
        for arg in node.args:
            arg.accept(self)

        # printf / scanf: alleen stdio check
        if node.name in ('printf', 'scanf'):
            if 'stdio.h' not in self.included_headers:
                self.error(
                    f"Functie '{node.name}' gebruikt zonder #include <stdio.h>."
                )
            return  # geen verdere checks voor variadische functies

        # zoek de functie op in de function_table
        func_entry = self.function_table.lookup(node.name)
        if func_entry is None:
            self.error(
                f"Aanroep van onbekende functie '{node.name}'. "
                f"Is de functie gedeclareerd of gedefinieerd?"
            )
            return

        # check: is de functie gedeclareerd/gedefinieerd VOOR de huidige aanroep?
        # Recursieve aanroepen zijn altijd geldig (zelfde index).
        func_pos = self.func_global_index.get(node.name, -1)
        if func_pos > self.current_global_index:
            self.error(
                f"Functie '{node.name}' wordt aangeroepen vóór de declaratie of definitie."
            )

        # check aantal argumenten
        expected = len(func_entry.params)
        actual   = len(node.args)
        if expected != actual:
            self.error(
                f"Functie '{node.name}' verwacht {expected} argument(en), "
                f"maar er worden {actual} meegegeven."
            )
            return

        # check types per argument
        for i, (arg, (exp_type, exp_depth)) in enumerate(zip(node.args, func_entry.params)):
            arg_type, arg_depth = self.get_type(arg)
            if arg_type == 'unknown':
                continue  # kan niet checken, al eerder een error gegeven
            if arg_depth != exp_depth:
                self.warning(
                    f"Argument {i+1} van '{node.name}': "
                    f"pointer diepte mismatch — "
                    f"verwacht {'*'*exp_depth}{exp_type}, "
                    f"gevonden {'*'*arg_depth}{arg_type}."
                )
            elif arg_type in TYPE_RANK and exp_type in TYPE_RANK:
                if TYPE_RANK[arg_type] > TYPE_RANK[exp_type]:
                    self.warning(
                        f"Argument {i+1} van '{node.name}': "
                        f"mogelijk precisieverlies — "
                        f"{arg_type} naar {exp_type}."
                    )