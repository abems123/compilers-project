# src/parser/semantic_analysis_visitor.py

from .ast_nodes import (
    LiteralNode, BinaryOpNode, UnaryOpNode,
    VariableNode, VarDeclNode, AssignNode,
    CastNode, TypeNode, BlockNode, ProgramNode
)
from .symbol_table import SymbolTable, SymbolEntry


# Type hiërarchie voor impliciete conversies (van arm naar rijk):
#   char < int < float
# Een "rijker" type kan een "armer" type bevatten zonder informatieverlies.
# Een "armer" type kan een "rijker" type NIET bevatten zonder informatieverlies
# → dat geeft een warning.
TYPE_RANK = {'char': 0, 'int': 1, 'float': 2}


def richer_type(a: str, b: str) -> str:
    """Geeft het rijkste van twee basistypes terug."""
    if TYPE_RANK.get(a, -1) >= TYPE_RANK.get(b, -1):
        return a
    return b


class SemanticAnalysisVisitor:
    """
    Loopt over de AST en controleert op semantische fouten en warnings.

    Fouten (errors): het programma is incorrect en kan niet gecompileerd worden.
    Warnings: het programma werkt misschien, maar er is mogelijk informatieverlies.

    Alle gevonden fouten en warnings worden verzameld in lijsten.
    Na de analyse kan je ze afdrukken met print_results().

    Gebruikte checks (verplicht volgens de assignment):
      ✓ Gebruik van een niet-gedeclareerde variabele
      ✓ Herhaalde declaratie van dezelfde variabele
      ✓ Assignment aan een const variabele
      ✓ Assignment aan een rvalue
      ✓ Impliciete conversie van rijker naar armer type (warning)
      ✓ Expliciete cast onderdrukt de warning
    """

    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors   = []   # lijst van foutmeldingen
        self.warnings = []   # lijst van waarschuwingen

    # --------------------------------------------------------
    # Hulpmethodes voor fout- en waarschuwingsrapportage
    # --------------------------------------------------------

    def error(self, msg: str, line: int = None):
        location = f"line {line}: " if line else ""
        self.errors.append(f"[ Error ] {location}{msg}")

    def warning(self, msg: str, line: int = None):
        location = f"line {line}: " if line else ""
        self.warnings.append(f"[ Warning ] {location}{msg}")

    def print_results(self):
        """Druk alle gevonden fouten en warnings af."""
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

    def get_type(self, node) -> tuple[str, int]:
        """
        Bepaalt het type van een expressie node.
        Geeft een tuple terug: (base_type, pointer_depth)

        Voorbeelden:
          LiteralNode(5, 'int')    → ('int', 0)
          VariableNode('x')        → type uit symbol table
          BinaryOpNode('+', ...)   → rijkste type van de twee operanden
          UnaryOpNode('&', x)      → (type van x, pointer_depth + 1)
          UnaryOpNode('*', ptr)    → (type van ptr, pointer_depth - 1)
        """
        if isinstance(node, LiteralNode):
            return (node.type_name, 0)

        elif isinstance(node, VariableNode):
            entry = self.symbol_table.lookup(node.name)
            if entry is None:
                return ('unknown', 0)
            return (entry.base_type, entry.pointer_depth)

        elif isinstance(node, BinaryOpNode):
            left_type,  left_depth  = self.get_type(node.left)
            right_type, right_depth = self.get_type(node.right)

            # vergelijkingsoperatoren geven altijd int terug (0 of 1)
            if node.op in ('==', '!=', '<', '>', '<=', '>=', '&&', '||'):
                return ('int', 0)

            # pointer arithmetic: int + pointer → pointer
            if left_depth > 0 or right_depth > 0:
                depth = max(left_depth, right_depth)
                base  = left_type if left_depth >= right_depth else right_type
                return (base, depth)

            return (richer_type(left_type, right_type), 0)

        elif isinstance(node, UnaryOpNode):
            operand_type, operand_depth = self.get_type(node.operand)

            if node.op == '&':
                # address-of: diepte + 1
                return (operand_type, operand_depth + 1)

            elif node.op == '*':
                # dereference: diepte - 1 (minimaal 0)
                return (operand_type, max(0, operand_depth - 1))

            elif node.op in ('prefix++', 'prefix--', 'suffix++', 'suffix--'):
                return (operand_type, operand_depth)

            else:
                return (operand_type, operand_depth)

        elif isinstance(node, CastNode):
            # het type van een cast is altijd het doeltype
            return (node.target_type.base_type, node.target_type.pointer_depth)

        return ('unknown', 0)

    # --------------------------------------------------------
    # Hulpmethode: is een node een geldige lvalue?
    # --------------------------------------------------------

    def is_lvalue(self, node) -> bool:
        """
        Een lvalue is een expressie waar je aan kan assignen.
        In C zijn dit:
          - een variabele: x
          - een pointer dereference: *ptr
        Geen lvalue (rvalue):
          - een literal: 5
          - een binaire operatie: x + y
          - een cast: (int) x
        """
        if isinstance(node, VariableNode):
            return True
        if isinstance(node, UnaryOpNode) and node.op == '*':
            return True
        return False

    # --------------------------------------------------------
    # STRUCTUUR
    # --------------------------------------------------------

    def visitProgram(self, node):
        # push een scope voor de main functie
        self.symbol_table.push_scope()
        node.body.accept(self)
        self.symbol_table.pop_scope()

    def visitBlock(self, node):
        # we pushen GEEN extra scope voor het main blok zelf,
        # want visitProgram doet dat al.
        # Als we later geneste blokken ondersteunen (if, while, enz.)
        # dan pushen we hier wel een scope.
        for stmt in node.statements:
            stmt.accept(self)

    # --------------------------------------------------------
    # DECLARATIES EN ASSIGNMENTS
    # --------------------------------------------------------

    def visitVarDecl(self, node):
        """
        Checks:
          1. Is de variabele al gedeclareerd in deze scope? (redeclaratie error)
          2. Is de initialisatiewaarde van het juiste type? (impliciete conversie warning)
        """
        # check 1: redeclaratie
        existing = self.symbol_table.lookup_current_scope(node.name)
        if existing is not None:
            self.error(
                f"Herhaalde declaratie van variabele '{node.name}'. "
                f"Eerste declaratie was van type '{existing.type_str()}'."
            )
            return

        # voeg toe aan symbol table
        entry = SymbolEntry(
            name          = node.name,
            base_type     = node.var_type.base_type,
            pointer_depth = node.var_type.pointer_depth,
            is_const      = node.var_type.is_const,
            is_defined    = node.value is not None
        )
        self.symbol_table.declare(entry)

        # check 2: initialisatiewaarde type (als die er is)
        if node.value is not None:
            node.value.accept(self)
            self._check_implicit_conversion(
                target_type  = node.var_type.base_type,
                target_depth = node.var_type.pointer_depth,
                value_node   = node.value,
                context      = f"declaratie van '{node.name}'"
            )

    def visitAssign(self, node):
        """
        Checks:
          1. Is de linkerkant een geldige lvalue?
          2. Is de linkerkant een const variabele?
          3. Is de rechterkant van het juiste type? (impliciete conversie)
        """
        # bezoek eerst de rechterkant
        node.value.accept(self)

        # check 1: is de linkerkant een lvalue?
        if not self.is_lvalue(node.target):
            self.error(
                f"Assignment aan een rvalue: '{_node_str(node.target)}'. "
                f"Je kan alleen assignen aan een variabele of pointer dereference."
            )
            return

        # check 2: is de linkerkant const?
        if isinstance(node.target, VariableNode):
            entry = self.symbol_table.lookup(node.target.name)
            if entry is None:
                self.error(f"Gebruik van niet-gedeclareerde variabele '{node.target.name}'.")
                return
            if entry.is_const and entry.pointer_depth == 0:
                # const int x → mag niet geassigned worden
                self.error(
                    f"Assignment aan const variabele '{node.target.name}' "
                    f"van type '{entry.type_str()}'."
                )
                return

            # check 3: impliciete conversie
            self._check_implicit_conversion(
                target_type  = entry.base_type,
                target_depth = entry.pointer_depth,
                value_node   = node.value,
                context      = f"assignment aan '{node.target.name}'"
            )

        elif isinstance(node.target, UnaryOpNode) and node.target.op == '*':
            # *ptr = value → check of de pointer zelf niet const is
            ptr_node = node.target.operand
            if isinstance(ptr_node, VariableNode):
                entry = self.symbol_table.lookup(ptr_node.name)
                if entry and entry.is_const:
                    self.error(
                        f"Assignment via const pointer '*{ptr_node.name}': "
                        f"de waarde waarnaar gewezen wordt is const."
                    )

    # --------------------------------------------------------
    # EXPRESSIES
    # --------------------------------------------------------

    def visitLiteral(self, node):
        # een literal heeft altijd een geldig type → niets te checken
        pass

    def visitVariable(self, node):
        """Check: is de variabele gedeclareerd?"""
        entry = self.symbol_table.lookup(node.name)
        if entry is None:
            self.error(f"Gebruik van niet-gedeclareerde variabele '{node.name}'.")

    def visitBinaryOp(self, node):
        """Bezoek beide operanden recursief."""
        node.left.accept(self)
        node.right.accept(self)

    def visitUnaryOp(self, node):
        """Bezoek de operand recursief."""
        node.operand.accept(self)

    def visitCast(self, node):
        """
        Een expliciete cast onderdrukt de impliciete conversie warning.
        We bezoeken wel de operand voor andere checks.
        """
        node.operand.accept(self)

    def visitType(self, node):
        pass

    # --------------------------------------------------------
    # Hulpmethode: impliciete conversie check
    # --------------------------------------------------------

    def _check_implicit_conversion(self, target_type: str, target_depth: int,
                                    value_node, context: str):
        """
        Geeft een warning als de waarde van een rijker type is dan het doeltype.

        Voorbeeld:
          float y = 3;     → geen warning (int → float is veilig)
          char c = 3.14;   → warning (float → char is mogelijk verlies)
          char c = (char) 3.14;  → geen warning (expliciete cast)
        """
        # expliciete cast onderdrukt de warning
        if isinstance(value_node, CastNode):
            return

        value_type, value_depth = self.get_type(value_node)

        # pointer depths moeten overeenkomen
        if target_depth != value_depth:
            # incompatibele pointer dieptes → warning
            # (de echte type mismatch errors komen later)
            if value_type != 'unknown':
                self.warning(
                    f"Mogelijk incompatibele types bij {context}: "
                    f"verwacht pointer diepte {target_depth}, "
                    f"maar kreeg diepte {value_depth}."
                )
            return

        # basistypes vergelijken (alleen voor niet-pointers)
        if target_depth == 0 and value_type != 'unknown':
            target_rank = TYPE_RANK.get(target_type, -1)
            value_rank  = TYPE_RANK.get(value_type, -1)

            if value_rank > target_rank:
                # rijker type naar armer type → warning
                self.warning(
                    f"Impliciete conversie bij {context}: "
                    f"'{value_type}' naar '{target_type}' "
                    f"kan leiden tot informatieverlies."
                )


def _node_str(node) -> str:
    """Geeft een leesbare string van een node voor in foutmeldingen."""
    if isinstance(node, LiteralNode):
        return str(node.value)
    if isinstance(node, VariableNode):
        return node.name
    if isinstance(node, BinaryOpNode):
        return f"({_node_str(node.left)} {node.op} {_node_str(node.right)})"
    if isinstance(node, UnaryOpNode):
        return f"{node.op}({_node_str(node.operand)})"
    return repr(node)