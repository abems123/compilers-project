# src/parser/semantic_analysis_visitor.py

from .ast_nodes import (
    LiteralNode, BinaryOpNode, UnaryOpNode,
    VariableNode, VarDeclNode, AssignNode,
    CastNode, TypeNode, BlockNode, ProgramNode,
    # Nieuw in assignment 3:
    CommentNode, ArrayDeclNode, ArrayInitNode,
    ArrayAccessNode, StringLiteralNode,
    FunctionCallNode, IncludeNode
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

    Assignment 3 voegt toe:
      - visitProgram      : leest includes → bepaalt stdio_included
      - visitArrayDecl    : redeclaratie check + initialisator lengte check
      - visitArrayAccess  : index type check (moet int zijn)
      - visitFunctionCall : stdio_included check voor printf/scanf
      - visitStringLiteral: altijd geldig, geen checks nodig
      - visitComment      : geen checks nodig
      - visitInclude      : registreert welke headers geïncludeerd zijn
      - get_type()        : uitgebreid voor ArrayAccessNode, StringLiteralNode,
                            FunctionCallNode
      - is_lvalue()       : uitgebreid voor ArrayAccessNode
    """

    def __init__(self):
        self.symbol_table   = SymbolTable()
        self.errors         = []
        self.warnings       = []

        # NIEUW: bijhouden welke headers geïncludeerd zijn
        # We gebruiken een set zodat we snel kunnen checken met 'in'
        self.included_headers = set()

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
        Geeft (base_type, pointer_depth) terug.

        NIEUW in assignment 3:
          - ArrayAccessNode → type van de elementen, pointer_depth - 1 per dimensie
          - StringLiteralNode → ('char', 1)  want een string is char*
          - FunctionCallNode  → ('int', 0)   want printf/scanf returnen int
        """
        if isinstance(node, LiteralNode):
            return (node.type_name, 0)

        elif isinstance(node, StringLiteralNode):
            # een string literal is een char* in C
            return ('char', 1)

        elif isinstance(node, VariableNode):
            entry = self.symbol_table.lookup(node.name)
            if entry is None:
                return ('unknown', 0)
            return (entry.base_type, entry.pointer_depth)

        elif isinstance(node, ArrayAccessNode):
            # het type van arr[i] is het element-type van de array
            # voor arr[i][j]: twee niveaus van indexering → base type
            #
            # We zoeken het type van de base array op via de symbol table.
            # De eenvoudigste aanpak: zoek de naam van de array op.
            # Voor arr[i]:       base = VariableNode('arr')
            # Voor arr[i][j]:    base = ArrayAccessNode(VariableNode('arr'), i)
            #
            # We navigeren naar de diepste VariableNode om de naam te vinden.
            base_name = self._get_array_base_name(node.array_expr)
            if base_name is None:
                return ('unknown', 0)

            entry = self.symbol_table.lookup(base_name)
            if entry is None:
                return ('unknown', 0)

            # het type van een array element is gewoon het base_type
            # zonder pointer depth (arrays zijn geen pointers in onze model)
            return (entry.base_type, 0)

        elif isinstance(node, FunctionCallNode):
            # printf en scanf returnen int in C
            return ('int', 0)

        elif isinstance(node, BinaryOpNode):
            left_type,  left_depth  = self.get_type(node.left)
            right_type, right_depth = self.get_type(node.right)

            if node.op in ('==', '!=', '<', '>', '<=', '>=', '&&', '||'):
                return ('int', 0)

            if left_depth > 0 or right_depth > 0:
                depth = max(left_depth, right_depth)
                base  = left_type if left_depth >= right_depth else right_type
                return (base, depth)

            return (richer_type(left_type, right_type), 0)

        elif isinstance(node, UnaryOpNode):
            operand_type, operand_depth = self.get_type(node.operand)

            if node.op == '&':
                return (operand_type, operand_depth + 1)
            elif node.op == '*':
                return (operand_type, max(0, operand_depth - 1))
            elif node.op in ('prefix++', 'prefix--', 'suffix++', 'suffix--'):
                return (operand_type, operand_depth)
            else:
                return (operand_type, operand_depth)

        elif isinstance(node, CastNode):
            return (node.target_type.base_type, node.target_type.pointer_depth)

        elif isinstance(node, ArrayInitNode):
            # een initialisator heeft geen type als expressie
            return ('unknown', 0)

        return ('unknown', 0)

    def _get_array_base_name(self, node) -> str | None:
        """
        Navigeert naar de diepste VariableNode in een ArrayAccessNode keten
        om de naam van de array te vinden.

        Voorbeelden:
          VariableNode('arr')                    → 'arr'
          ArrayAccessNode(VariableNode('m'), i)  → 'm'
          ArrayAccessNode(ArrayAccessNode(...))  → recursief
        """
        if isinstance(node, VariableNode):
            return node.name
        elif isinstance(node, ArrayAccessNode):
            return self._get_array_base_name(node.array_expr)
        return None

    # --------------------------------------------------------
    # Hulpmethode: is een node een geldige lvalue?
    # --------------------------------------------------------

    def is_lvalue(self, node) -> bool:
        """
        NIEUW: ArrayAccessNode is een geldige lvalue.
        arr[i] = 5 is geldig.
        arr[i][j] = 5 is ook geldig.
        """
        if isinstance(node, VariableNode):
            return True
        if isinstance(node, UnaryOpNode) and node.op == '*':
            return True
        # NIEUW: array element toegang is een lvalue
        if isinstance(node, ArrayAccessNode):
            return True
        return False

    # --------------------------------------------------------
    # STRUCTUUR
    # --------------------------------------------------------

    def visitProgram(self, node):
        """
        NIEUW: verwerk de includes vóór de rest van het programma.
        Zo weet de rest van de analyse of stdio.h beschikbaar is.
        """
        # stap 1: verwerk alle includes
        for inc in node.includes:
            inc.accept(self)

        # stap 2: verwerk de body
        self.symbol_table.push_scope()
        node.body.accept(self)
        self.symbol_table.pop_scope()

    def visitInclude(self, node):
        """
        NIEUW: registreer de geïncludeerde header.
        De naam ('stdio.h') wordt toegevoegd aan included_headers.
        """
        self.included_headers.add(node.header)

    def visitBlock(self, node):
        for stmt in node.statements:
            stmt.accept(self)

    # --------------------------------------------------------
    # DECLARATIES EN ASSIGNMENTS
    # --------------------------------------------------------

    def visitVarDecl(self, node):
        """
        Ongewijzigd van assignment 2.
        """
        existing = self.symbol_table.lookup_current_scope(node.name)
        if existing is not None:
            self.error(
                f"Herhaalde declaratie van variabele '{node.name}'. "
                f"Eerste declaratie was van type '{existing.type_str()}'."
            )
            return

        entry = SymbolEntry(
            name          = node.name,
            base_type     = node.var_type.base_type,
            pointer_depth = node.var_type.pointer_depth,
            is_const      = node.var_type.is_const,
            is_defined    = node.value is not None
        )
        self.symbol_table.declare(entry)

        if node.value is not None:
            node.value.accept(self)
            self._check_implicit_conversion(
                target_type  = node.var_type.base_type,
                target_depth = node.var_type.pointer_depth,
                value_node   = node.value,
                context      = f"declaratie van '{node.name}'"
            )

    def visitArrayDecl(self, node):
        """
        NIEUW: verwerk een array declaratie.

        Checks:
          1. Redeclaratie in dezelfde scope
          2. Als er een initialisator is:
             a. Controleer dat de lengte overeenkomt met de eerste dimensie
             b. Voor 2D: controleer ook de lengte van elke rij
             c. Bezoek alle elementen voor verdere checks

        EDGE CASE: int arr[3] = {} → lengte 0 ≠ 3 → error
        EDGE CASE: int arr[3] = {1, 2} → lengte 2 ≠ 3 → error
        EDGE CASE: int arr[2][3] = {{1,2,3},{4,5}} → tweede rij heeft 2 ≠ 3 → error
        """
        # check 1: redeclaratie
        existing = self.symbol_table.lookup_current_scope(node.name)
        if existing is not None:
            self.error(
                f"Herhaalde declaratie van array '{node.name}'. "
                f"Eerste declaratie was van type '{existing.type_str()}'."
            )
            return

        # voeg toe aan symbol table MET array info
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

        # check 2: initialisator
        if node.initializer is not None:
            self._check_array_init(node.initializer, node.dimensions, node.name)

    def _check_array_init(self, init_node: ArrayInitNode,
                          dimensions: list, array_name: str):
        """
        Controleert recursief de lengte van een array initialisator.

        Parameters:
          init_node  : de ArrayInitNode die we controleren
          dimensions : de verwachte dimensies op dit niveau, bv. [2, 3]
          array_name : naam van de array, voor foutmeldingen

        Logica:
          - dimensions[0] is de verwachte lengte op dit niveau
          - als dimensions meer dan één element heeft, zijn de kinderen
            zelf ArrayInitNodes (geneste rijen) die we recursief checken

        EDGE CASE: lege initialisator {} heeft lengte 0.
        EDGE CASE: geneste initialisator met verkeerde rij-lengte.
        EDGE CASE: element is een expressie terwijl een rij verwacht wordt,
          of omgekeerd — we checken dit impliciet via de type checks.
        """
        expected_len = dimensions[0]
        actual_len   = len(init_node.elements)

        # check: het aantal elementen op dit niveau
        if actual_len != expected_len:
            self.error(
                f"Verkeerde initialisator lengte voor array '{array_name}': "
                f"verwacht {expected_len} element(en), maar kreeg {actual_len}."
            )
            # na een lengte-error stoppen we met verdere structuur-checks
            # voor dit niveau — de lengte-error zegt al genoeg.
            return

        # als er meer dimensies zijn, zijn de elementen geneste ArrayInitNodes
        if len(dimensions) > 1:
            for i, elem in enumerate(init_node.elements):
                if isinstance(elem, ArrayInitNode):
                    # recursief: check de rij met de resterende dimensies
                    self._check_array_init(elem, dimensions[1:], f"{array_name}[{i}]")
                else:
                    # een expressie op een plek waar een rij verwacht wordt
                    self.error(
                        f"Element {i} van array '{array_name}' moet een "
                        f"rij-initialisator zijn ({{...}}), maar is een expressie."
                    )
        else:
            # 1D niveau: de elementen zijn gewone expressies
            for elem in init_node.elements:
                if isinstance(elem, ArrayInitNode):
                    # een geneste {{...}} op een plek waar een waarde verwacht wordt
                    self.error(
                        f"Onverwachte geneste initialisator in 1D array '{array_name}'."
                    )
                else:
                    # bezoek de expressie voor verdere checks (bv. ongedeclareerde var)
                    elem.accept(self)

    def visitAssign(self, node):
        """
        Uitgebreid met ArrayAccessNode als geldige lvalue.
        De rest is ongewijzigd van assignment 2.
        """
        node.value.accept(self)

        if not self.is_lvalue(node.target):
            self.error(
                f"Assignment aan een rvalue: '{_node_str(node.target)}'. "
                f"Je kan alleen assignen aan een variabele of pointer dereference."
            )
            return

        if isinstance(node.target, VariableNode):
            entry = self.symbol_table.lookup(node.target.name)
            if entry is None:
                self.error(f"Gebruik van niet-gedeclareerde variabele '{node.target.name}'.")
                return

            # EDGE CASE: je kan niet een scalar assignen aan een array naam
            # bv. arr = 5 is ongeldig (arr is een array, geen scalar)
            if entry.is_array:
                self.error(
                    f"Kan niet assignen aan array '{node.target.name}': "
                    f"arrays zijn geen lvalues. Gebruik een index: {node.target.name}[i]."
                )
                return

            if entry.is_const and entry.pointer_depth == 0:
                self.error(
                    f"Assignment aan const variabele '{node.target.name}' "
                    f"van type '{entry.type_str()}'."
                )
                return

            self._check_implicit_conversion(
                target_type  = entry.base_type,
                target_depth = entry.pointer_depth,
                value_node   = node.value,
                context      = f"assignment aan '{node.target.name}'"
            )

        elif isinstance(node.target, ArrayAccessNode):
            # arr[i] = value → check het type van de array elementen
            base_name = self._get_array_base_name(node.target)
            if base_name:
                entry = self.symbol_table.lookup(base_name)
                if entry:
                    self._check_implicit_conversion(
                        target_type  = entry.base_type,
                        target_depth = 0,
                        value_node   = node.value,
                        context      = f"assignment aan '{base_name}[...]'"
                    )

        elif isinstance(node.target, UnaryOpNode) and node.target.op == '*':
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
        pass

    def visitStringLiteral(self, node):
        # een string literal is altijd geldig — geen checks nodig
        pass

    def visitComment(self, node):
        # comments hoeven niet geanalyseerd te worden
        pass

    def visitVariable(self, node):
        """Check: is de variabele gedeclareerd?"""
        entry = self.symbol_table.lookup(node.name)
        if entry is None:
            self.error(f"Gebruik van niet-gedeclareerde variabele '{node.name}'.")

    def _visit_array_indices(self, node):
        """
        Bezoekt recursief alleen de INDEX expressies in een ArrayAccess keten,
        maar NIET de base VariableNode zelf.

        Waarom? Als we node.array_expr.accept(self) aanroepen, vuurt
        visitVariable een "niet-gedeclareerde variabele" error én dan vuren
        we zelf ook een "niet-gedeclareerde array" error → dubbele melding.

        Voor arr[i]:       bezoek i
        Voor arr[i][j]:    bezoek i én j (recursief)
        """
        # bezoek de index van dit niveau
        node.index.accept(self)
        # als de array_expr zelf ook een ArrayAccess is (bv. arr[i][j]),
        # bezoek dan ook de indices daarin
        if isinstance(node.array_expr, ArrayAccessNode):
            self._visit_array_indices(node.array_expr)

    def visitArrayAccess(self, node):
        """
        Checks voor array element toegang.

        1. De base variabele moet gedeclareerd en een array zijn
        2. De index moet van type int zijn

        We roepen node.array_expr.accept(self) NIET aan om dubbele
        "niet-gedeclareerde" errors te vermijden — zie _visit_array_indices.
        """
        # stap 1: bezoek alleen de indices (niet de base VariableNode)
        self._visit_array_indices(node)

        # stap 2: controleer of de base een gedeclareerde array is
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

        # stap 3: type check van de outerste index — moet int zijn
        # (de index is al bezocht via _visit_array_indices in stap 1)
        index_type, index_depth = self.get_type(node.index)

        # EDGE CASE: pointer of array als index → fout
        if index_depth > 0:
            self.error(
                f"Array index mag geen pointer zijn. "
                f"Gevonden type: {'*' * index_depth}{index_type}."
            )
        # EDGE CASE: float als index → fout
        elif index_type == 'float':
            self.error(
                f"Array index moet van type 'int' zijn, "
                f"maar '{index_type}' gevonden."
            )
        # EDGE CASE: char als index → warning (technisch geldig maar ongewoon)
        elif index_type == 'char':
            self.warning(
                f"Array index is van type 'char'. "
                f"Overweeg een expliciete cast naar 'int'."
            )
        # 'unknown' → al een error gemeld voor de ongedeclareerde variabele

    def visitBinaryOp(self, node):
        node.left.accept(self)
        node.right.accept(self)

    def visitUnaryOp(self, node):
        node.operand.accept(self)

    def visitCast(self, node):
        node.operand.accept(self)

    def visitType(self, node):
        pass

    def visitFunctionCall(self, node):
        """
        NIEUW: checks voor printf en scanf.

        Checks:
          1. Is stdio.h geïncludeerd? Zo niet → error
          2. Is de functienaam bekend? (printf of scanf)
             Andere functienamen → error (we ondersteunen geen andere functies)
          3. Bezoek alle argumenten voor verdere checks

        EDGE CASE: printf() zonder argumenten → technisch geen error hier,
          de format string check is optioneel (buiten scope van de opdracht)
        EDGE CASE: scanf met &x als argument → UnaryOpNode('&', ...)
          → wordt gewoon als expressie bezocht → geen speciale behandeling nodig
        """
        # check 1: stdio.h vereist voor printf en scanf
        if node.name in ('printf', 'scanf'):
            if 'stdio.h' not in self.included_headers:
                self.error(
                    f"Gebruik van '{node.name}' zonder '#include <stdio.h>'. "
                    f"Voeg '#include <stdio.h>' toe bovenaan het bestand."
                )
                # we gaan door om ook de argumenten te checken

        # check 2: onbekende functienamen
        # we ondersteunen alleen printf en scanf in deze compiler.
        # de 'else' hier wordt bereikt als node.name NIET 'printf' of 'scanf' is.
        else:
            self.error(
                f"Onbekende functie '{node.name}'. "
                f"Alleen 'printf' en 'scanf' worden ondersteund."
            )

        # check 3: bezoek alle argumenten
        for arg in node.args:
            arg.accept(self)

    # --------------------------------------------------------
    # Hulpmethode: impliciete conversie check
    # --------------------------------------------------------

    def _check_implicit_conversion(self, target_type: str, target_depth: int,
                                    value_node, context: str):
        """
        Ongewijzigd van assignment 2.
        Geeft een warning als de waarde van een rijker type is dan het doeltype.
        """
        if isinstance(value_node, CastNode):
            return

        value_type, value_depth = self.get_type(value_node)

        if target_depth != value_depth:
            if value_type != 'unknown':
                self.warning(
                    f"Mogelijk incompatibele types bij {context}: "
                    f"verwacht pointer diepte {target_depth}, "
                    f"maar kreeg diepte {value_depth}."
                )
            return

        if target_depth == 0 and value_type != 'unknown':
            target_rank = TYPE_RANK.get(target_type, -1)
            value_rank  = TYPE_RANK.get(value_type, -1)

            if value_rank > target_rank:
                self.warning(
                    f"Impliciete conversie bij {context}: "
                    f"'{value_type}' naar '{target_type}' "
                    f"kan leiden tot informatieverlies."
                )


def _node_str(node) -> str:
    """Geeft een leesbare string van een node voor in foutmeldingen."""
    if isinstance(node, LiteralNode):
        return str(node.value)
    if isinstance(node, StringLiteralNode):
        return f'"{node.value}"'
    if isinstance(node, VariableNode):
        return node.name
    if isinstance(node, ArrayAccessNode):
        return f"{_node_str(node.array_expr)}[{_node_str(node.index)}]"
    if isinstance(node, BinaryOpNode):
        return f"({_node_str(node.left)} {node.op} {_node_str(node.right)})"
    if isinstance(node, UnaryOpNode):
        return f"{node.op}({_node_str(node.operand)})"
    return repr(node)