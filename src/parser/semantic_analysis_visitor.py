# src/parser/semantic_analysis_visitor.py

from .ast_nodes import (
    LiteralNode, BinaryOpNode, UnaryOpNode,
    VariableNode, VarDeclNode, AssignNode,
    CastNode, TypeNode, BlockNode, ProgramNode,
    # Assignment 3:
    CommentNode, ArrayDeclNode, ArrayInitNode,
    ArrayAccessNode, StringLiteralNode,
    FunctionCallNode, IncludeNode,
    # Assignment 4 (nieuw):
    EnumDefNode, IfNode, WhileNode,
    BreakNode, ContinueNode, ScopeNode
)
from .symbol_table import SymbolTable, SymbolEntry


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

    Assignment 4 voegt toe:
      - visitProgram   : verwerkt nu ook enums vóór de body
      - visitEnumDef   : registreert labels als const int in de globale scope
      - visitIf        : push/pop scope voor beide takken
      - visitWhile     : push/pop scope voor body, bijhouden loop_depth
      - visitBreak     : check of we in een lus of switch zitten
      - visitContinue  : check of we in een lus zitten (NIET switch)
      - visitScope     : push/pop scope voor anonieme blokken
      - visitVarDecl   : uitgebreid: enum type check
      - visitBlock     : ongewijzigd (push/pop scope zit in de callers)

    SCOPE STRATEGIE:
      - visitProgram opent de globale scope (push_scope)
      - visitIf/visitWhile/visitScope openen elk een nieuwe scope (push/pop)
      - visitBlock zelf doet GEEN push/pop meer — dat doen de callers.
        Zo voorkomt je dat main() een dubbele scope krijgt.

    LOOP TRACKING:
      - self.loop_depth  : int — hoe diep zitten we in lussen (while/for)?
      - self.switch_depth: int — hoe diep zitten we in switch statements?
      break  is geldig als loop_depth > 0 OF switch_depth > 0
      continue is geldig als loop_depth > 0 (NIET in switch alleen)

    ENUM TRACKING:
      - self.enum_types: dict van enum-naam → lijst van labels
        Zodat we bij 'enum Status x = BUSY' kunnen checken of BUSY geldig is.
      - Enum labels worden als SymbolEntry met is_const=True in de
        GLOBALE scope geregistreerd (scope index 0).
    """

    def __init__(self):
        self.symbol_table    = SymbolTable()
        self.errors          = []
        self.warnings        = []
        self.included_headers = set()

        # NIEUW in assignment 4:
        self.loop_depth   = 0   # teller voor while/for nesting
        self.switch_depth = 0   # teller voor switch nesting
        self.enum_types   = {}  # enum-naam → lijst van label-strings

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
            return ('int', 0)

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
        NIEUW in assignment 4: verwerk enums vóór includes en body,
        zodat enum labels als geldige const int variabelen beschikbaar
        zijn voor de rest van de analyse.

        Volgorde:
          1. Open globale scope
          2. Verwerk includes (bepaal stdio_included)
          3. Verwerk enum definities (registreer labels in globale scope)
          4. Verwerk de body van main()
          5. Sluit globale scope
        """
        self.symbol_table.push_scope()

        # includes
        for inc in node.includes:
            inc.accept(self)

        # NIEUW: enum definities
        for enum_node in node.enums:
            enum_node.accept(self)

        # body van main (geen extra push_scope hier — de body is al in de globale scope)
        node.body.accept(self)

        self.symbol_table.pop_scope()

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

    def visitFunctionCall(self, node):
        """Ongewijzigd van assignment 3."""
        if node.name in ('printf', 'scanf'):
            if 'stdio.h' not in self.included_headers:
                self.error(
                    f"Functie '{node.name}' gebruikt zonder #include <stdio.h>."
                )
        for arg in node.args:
            arg.accept(self)

    def visitInclude(self, node):
        self.included_headers.add(node.header)