# src/parser/constant_folding_visitor.py

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


class ConstantFoldingVisitor:
    """
    Doet twee dingen in één pass over de AST:

    1. Constant Folding: berekent expressies met alleen literals op compile-time.
       Voorbeeld: 3 + 4  →  LiteralNode(7)

    2. Constant Propagation: vervangt variabelen met bekende waarden door hun literal.
       Voorbeeld: const int x = 5; int y = x + 3;  →  int y = 8;

    Assignment 4 uitbreiding:
      - Enum labels worden als constante int waarden geregistreerd (0, 1, 2, ...)
        en kunnen dus gevouwen worden in expressies: OFFLINE + 1 → 3
      - If/while/for/scope: known_values worden per scope bijgehouden.
        Een variabele die ALLEEN in een if-tak verandert, is na het if-statement
        niet meer betrouwbaar bekend → we verwijderen hem uit known_values.
      - BreakNode, ContinueNode: worden ongewijzigd doorgegeven.
      - ScopeNode: behandeld als een blok met eigen scope voor known_values.

    SCOPE-STRATEGIE voor known_values:
      Bij elk blok met een eigen scope (if-tak, while-body, scope-node)
      slaan we een SNAPSHOT op van known_values vóór het blok.
      Na het blok vergelijken we: waarden die veranderd zijn worden
      VERWIJDERD uit known_values (conservatief correcte aanpak).

      Waarom conservatief?
        int x = 5;
        if (cond) { x = 10; }
        // hier weten we NIET of x 5 of 10 is (hangt af van cond op runtime)
        // dus x verwijderen we uit known_values

      Enum labels en globale consts worden NOOIT verwijderd uit known_values
      (ze zijn immutable per definitie).
    """

    def __init__(self):
        # dict van variabelenaam → LiteralNode met de bekende waarde
        self.known_values = {}

        # dict van variabelenaam → bool (is het een const variabele?)
        self.is_const = {}

    # ============================================================
    # HULPMETHODE: snapshot voor scope-correcte propagation
    # ============================================================

    def _snapshot(self) -> dict:
        """Geeft een kopie van known_values terug (voor scope-herstel)."""
        return dict(self.known_values)

    def _invalidate_changed(self, snapshot: dict):
        """
        Verwijdert uit known_values alle namen die veranderd zijn t.o.v. snapshot.
        Zo weet de code na een if/while dat die variabelen niet meer betrouwbaar zijn.

        EDGE CASE: variabelen die IN het blok NIEUW gedeclareerd zijn en
        dus NIET in de snapshot staan, worden ook verwijderd — ze zijn
        buiten het blok niet zichtbaar (out-of-scope).

        EDGE CASE: const variabelen en enum labels (is_const=True) worden
        NOOIT verwijderd — ze kunnen toch niet veranderd zijn.
        """
        keys_to_remove = []
        for name in list(self.known_values.keys()):
            if self.is_const.get(name, False):
                continue  # consts en enum labels blijven altijd geldig
            if name not in snapshot:
                keys_to_remove.append(name)  # nieuw in dit blok → niet zichtbaar buiten
            elif self.known_values[name] != snapshot[name]:
                keys_to_remove.append(name)  # veranderd in dit blok → niet betrouwbaar
        for name in keys_to_remove:
            del self.known_values[name]

    def _collect_assigned_vars(self, node) -> set:
        """
        Verzamelt alle variabelenamen die ergens in een AST-deelboom
        worden geassigned (via AssignNode of VarDeclNode).

        Wordt gebruikt door visitWhile om vóór het vouwen van de conditie
        al te weten welke vars onbetrouwbaar zijn — zodat x < 10 NIET
        gevouwen wordt naar 1 alleen omdat x toevallig vóór de lus
        een bekende waarde had.

        EDGE CASE: geneste if/while/scope worden ook doorzocht.
        EDGE CASE: prefix++/suffix++ zijn ook assignments.
        EDGE CASE: array assignments (arr[i] = x) worden genegeerd
                   (array elementen zitten toch niet in known_values).
        """
        assigned = set()

        if isinstance(node, AssignNode):
            if isinstance(node.target, VariableNode):
                assigned.add(node.target.name)
            assigned |= self._collect_assigned_vars(node.value)

        elif isinstance(node, VarDeclNode):
            assigned.add(node.name)
            if node.value is not None:
                assigned |= self._collect_assigned_vars(node.value)

        elif isinstance(node, BlockNode):
            for stmt in node.statements:
                assigned |= self._collect_assigned_vars(stmt)

        elif isinstance(node, IfNode):
            assigned |= self._collect_assigned_vars(node.then_block)
            if node.else_block is not None:
                assigned |= self._collect_assigned_vars(node.else_block)

        elif isinstance(node, WhileNode):
            assigned |= self._collect_assigned_vars(node.body)

        elif isinstance(node, ScopeNode):
            assigned |= self._collect_assigned_vars(node.body)

        elif isinstance(node, UnaryOpNode):
            if node.op in ('prefix++', 'prefix--', 'suffix++', 'suffix--'):
                if isinstance(node.operand, VariableNode):
                    assigned.add(node.operand.name)

        return assigned

    # ============================================================
    # STRUCTUUR: program, block
    # ============================================================

    def visitProgram(self, node):
        """
        Assignment 5: itereer over globals in plaats van vaste body+enums structuur.

        Enum definities worden EERST verwerkt zodat hun labels beschikbaar
        zijn als constante waarden voor de rest.
        """
        # Pass 1: registreer enum labels als constanten
        for item in node.globals:
            if isinstance(item, EnumDefNode):
                item.accept(self)

        # Pass 2: verwerk alle globals (functiedefinities, variabelen, etc.)
        new_globals = []
        for item in node.globals:
            if isinstance(item, EnumDefNode):
                new_globals.append(item)  # al verwerkt, ongewijzigd bewaren
            else:
                new_globals.append(item.accept(self))

        return ProgramNode(new_globals)

    # ── Assignment 5: nieuwe nodes ────────────────────────────────────────────

    def visitFunctionDef(self, node):
        """
        Vouw de body van de functie. Parameters zijn niet constant,
        dus we bewaren een schone known_values snapshot per functie.

        EDGE CASE: known_values van globale consts/enums blijven geldig binnen
        de functie — die zijn immutable. Lokale variabelen worden na de
        functie weer geleegd (andere scope).
        """
        snapshot = self._snapshot()

        new_params = node.params   # params veranderen niet bij folding
        new_body   = node.body.accept(self)

        # herstel known_values: lokale vars van de functie weggooien
        self._invalidate_changed(snapshot)

        return FunctionDefNode(node.return_type, node.name, new_params, new_body)

    def visitFunctionDecl(self, node):
        return node  # forward declarations veranderen niet

    def visitReturn(self, node):
        """Vouw de return-waarde als die een constante expressie is."""
        if node.value is not None:
            new_value = node.value.accept(self)
        else:
            new_value = None
        return ReturnNode(new_value)

    def visitDefine(self, node):
        return node  # defines veranderen niet

    def visitIncludeFile(self, node):
        return node  # includes veranderen niet

    def visitParam(self, node):
        return node  # parameters veranderen niet

    def visitBlock(self, node):
        new_statements = []
        for stmt in node.statements:
            new_stmt = stmt.accept(self)
            new_statements.append(new_stmt)
        return BlockNode(new_statements)

    # ============================================================
    # NIEUW: ENUM DEFINITIE
    # ============================================================

    def visitEnumDef(self, node):
        """
        Registreer alle enum labels als constante int waarden.

        Voorbeeld:
          enum Status { READY, BUSY, OFFLINE }
          → known_values['READY']   = LiteralNode(0, 'int')
          → known_values['BUSY']    = LiteralNode(1, 'int')
          → known_values['OFFLINE'] = LiteralNode(2, 'int')

        Ze worden ook als 'const' gemarkeerd zodat _invalidate_changed()
        ze nooit verwijdert.

        EDGE CASE: als twee enums dezelfde labelnaam hebben, overschrijft
        de laatste. De semantic analysis zal dit al als error melden,
        dus hier hoeven we het niet te checken.
        """
        for i, label in enumerate(node.labels):
            literal = LiteralNode(i, 'int')
            self.known_values[label] = literal
            self.is_const[label]     = True   # nooit invalideren

        return node  # EnumDefNode zelf verandert niet

    # ============================================================
    # NIEUW: CONTROL FLOW NODES
    # ============================================================

    def visitIf(self, node):
        """
        Vouw de conditie. Bezoek beide takken conservatief:
        na het if-statement invalideren we waarden die in een tak
        veranderd kunnen zijn.

        EDGE CASE: als de conditie een constante is (bv. if (1) { ... }),
        kunnen we in principe de dode tak weggooien. We doen dit NIET —
        dat is dead code elimination, een aparte optimalisatie. We vouwen
        alleen de conditie-expressie zelf.

        SCOPE: snapshot vóór then-tak, snapshot vóór else-tak, daarna
        invalideer wat in BEIDE takken mogelijk veranderd is.
        """
        new_condition = node.condition.accept(self)

        # then-tak: snapshot → bezoek → vergelijk
        snap_before_then = self._snapshot()
        new_then = node.then_block.accept(self)
        snap_after_then = self._snapshot()

        # herstel naar voor-then snapshot voor de else-tak
        self.known_values = dict(snap_before_then)

        # else-tak (optioneel)
        new_else = None
        if node.else_block is not None:
            snap_before_else = self._snapshot()
            new_else = node.else_block.accept(self)
            snap_after_else = self._snapshot()
            # herstel naar voor-else
            self.known_values = dict(snap_before_else)
        else:
            snap_after_else = snap_before_then  # geen else → alsof er niets veranderd is

        # invalideer alles wat in then OF else mogelijk veranderd is
        # We doen dit door te kijken wat ná then of ná else anders is
        # dan vóór het if-statement (= snap_before_then).
        snap_before_if = snap_before_then
        for name in list(self.known_values.keys()):
            if self.is_const.get(name, False):
                continue
            val_before = snap_before_if.get(name)
            val_after_then = snap_after_then.get(name)
            val_after_else = snap_after_else.get(name)
            # als de waarde in een van de takken veranderd kan zijn → invalideer
            if val_after_then != val_before or val_after_else != val_before:
                del self.known_values[name]

        return IfNode(new_condition, new_then, new_else)

    def visitWhile(self, node):
        """
        Vouw de conditie. De body behandelen we conservatief:
        we veronderstellen dat ALLE niet-const variabelen die in de
        body veranderd worden, na de lus onbekend zijn.

        WAAROM niet propageren door lussen?
          int x = 0;
          while (x < 10) { x = x + 1; }
          // hier weten we NIET wat x is na de lus (runtime bepaalt dit)

        AANPAK: snapshot vóór de body → bezoek → invalideer wat veranderd is.

        EDGE CASE: de conditie wordt gevouwen MET de waarden van VÓÓR de lus.
        Dit is correct: de eerste evaluatie van de conditie gebruikt die waarden.
        Maar de conditie kan ook veranderen tijdens de lus (x verandert) —
        dat is runtime logica die we hier niet kunnen volgen.

        EDGE CASE: WhileNode.update (voor for-lussen) wordt ook gevouwen.
        """
        # snapshot vóór de lus
        snap_before = self._snapshot()

        # STAP 1: verzamel alle vars die in de body (en update) geassigned worden
        modified = self._collect_assigned_vars(node.body)
        if node.update is not None:
            modified |= self._collect_assigned_vars(node.update)

        # STAP 2: verwijder die vars UIT known_values VÓÓR het vouwen van de conditie.
        # Zo wordt x < 10 NIET gevouwen naar 1 alleen omdat x = 8 vóór de lus bekend was.
        # Consts en enum labels (is_const=True) blijven altijd staan.
        for name in modified:
            if not self.is_const.get(name, False):
                self.known_values.pop(name, None)

        # STAP 3: vouw de conditie (x is nu onbekend -> blijft als expressie staan)
        new_condition = node.condition.accept(self)

        # STAP 4: vouw de body
        new_body = node.body.accept(self)

        # STAP 5: vouw de update expressie (kan None zijn)
        new_update = node.update.accept(self) if node.update is not None else None

        # STAP 6: invalideer wat in de body veranderd kan zijn (voor na de lus)
        self._invalidate_changed(snap_before)

        return WhileNode(new_condition, new_body, new_update)

    def visitBreak(self, node):
        """Break nodes worden ongewijzigd doorgegeven."""
        return node

    def visitContinue(self, node):
        """Continue nodes worden ongewijzigd doorgegeven."""
        return node

    def visitScope(self, node):
        """
        Anonieme scope: behandel als een blok met eigen known_values scope.
        Variabelen gedeclareerd IN de scope zijn daarna niet meer zichtbaar.

        EDGE CASE: variabelen van BUITEN de scope kunnen WEL gelezen worden
        (propagation van buiten naar binnen is OK), maar wijzigingen van
        BINNEN invalideren ze voor gebruik BUITEN.
        """
        snap_before = self._snapshot()
        new_body = node.body.accept(self)
        self._invalidate_changed(snap_before)
        return ScopeNode(new_body)

    # ============================================================
    # DECLARATIES EN ASSIGNMENTS (ongewijzigd van assignment 3)
    # ============================================================

    def visitVarDecl(self, node):
        if node.value is not None:
            new_value = node.value.accept(self)
        else:
            new_value = None

        # impliciete float conversie: int literal in float variabele
        if (isinstance(new_value, LiteralNode)
                and node.var_type.base_type == 'float'
                and new_value.type_name == 'int'):
            new_value = LiteralNode(float(new_value.value), 'float')

        if isinstance(new_value, LiteralNode):
            self.known_values[node.name] = new_value
            self.is_const[node.name] = node.var_type.is_const

        # Const casting: als het adres van een variabele (&x) wordt opgeslagen
        # in een pointer (const of niet), kan die variabele later via const casting
        # gewijzigd worden. Daarom: verwijder x uit known_values zodra &x
        # in een pointer terecht komt — ook als het via een const pointer gaat.
        #
        # Voorbeeld: const int* cp = &x  →  x invalideren
        #            int* p = &x         →  x invalideren
        # Zo voorkomt we dat printf("%d", x) na *p=99 toch 5 afdrukt.
        if (node.var_type.pointer_depth > 0
                and isinstance(new_value, UnaryOpNode)
                and new_value.op == '&'
                and isinstance(new_value.operand, VariableNode)):
            aliased = new_value.operand.name
            # invalideer: via deze pointer (of een cast ervan) kan de waarde wijzigen
            self.known_values.pop(aliased, None)
            self.is_const[aliased] = False  # niet meer als const behandelen

        return VarDeclNode(node.var_type, node.name, new_value)

    def visitAssign(self, node):
        new_value = node.value.accept(self)

        if isinstance(node.target, VariableNode):
            name = node.target.name
            if not self.is_const.get(name, False):
                if isinstance(new_value, LiteralNode):
                    self.known_values[name] = new_value
                else:
                    self.known_values.pop(name, None)

        return AssignNode(node.target, new_value)

    # ============================================================
    # ARRAY NODES (ongewijzigd van assignment 3)
    # ============================================================

    def visitArrayDecl(self, node):
        if node.initializer is not None:
            new_init = node.initializer.accept(self)
        else:
            new_init = None
        return ArrayDeclNode(node.var_type, node.name, node.dimensions, new_init)

    def visitArrayInit(self, node):
        new_elements = [elem.accept(self) for elem in node.elements]
        return ArrayInitNode(new_elements)

    def visitArrayAccess(self, node):
        new_array_expr = node.array_expr.accept(self)
        new_index      = node.index.accept(self)
        return ArrayAccessNode(new_array_expr, new_index)

    # ============================================================
    # COMMENT, INCLUDE, STRING, FUNCTIONCALL (ongewijzigd)
    # ============================================================

    def visitComment(self, node):
        return node

    def visitInclude(self, node):
        return node

    def visitStringLiteral(self, node):
        return node

    def visitFunctionCall(self, node):
        new_args = [arg.accept(self) for arg in node.args]

        # EDGE CASE: als een argument &x is (adres-van), dan geeft de aanroeper
        # de pointer door aan de functie. De functie KAN x wijzigen via *ptr.
        # We weten op compile-time niet of dat ook echt gebeurt, dus conservatief:
        # verwijder x uit known_values zodat we x daarna niet meer fout propageren.
        for arg in node.args:
            if (isinstance(arg, UnaryOpNode)
                    and arg.op == '&'
                    and isinstance(arg.operand, VariableNode)):
                self.known_values.pop(arg.operand.name, None)

        return FunctionCallNode(node.name, new_args)

    # ============================================================
    # CONSTANT PROPAGATION: variabelen vervangen door hun waarde
    # ============================================================

    def visitVariable(self, node):
        """
        Vervang variabelen door hun bekende waarde als die beschikbaar is.

        NIEUW: enum labels staan ook in known_values (als const int),
        dus READY wordt automatisch gevouwen naar LiteralNode(0, 'int').

        EDGE CASE: als de variabele niet in known_values staat,
        geven we de VariableNode ongewijzigd terug.
        """
        if node.name in self.known_values:
            return self.known_values[node.name]
        return node

    # ============================================================
    # EXPRESSIES: folding (ongewijzigd van assignment 2/3)
    # ============================================================

    def visitLiteral(self, node):
        return node

    def visitBinaryOp(self, node):
        left  = node.left.accept(self)
        right = node.right.accept(self)

        if isinstance(left, LiteralNode) and isinstance(right, LiteralNode):
            l = left.value
            r = right.value

            try:
                if node.op == '+':
                    resultaat = l + r
                elif node.op == '-':
                    resultaat = l - r
                elif node.op == '*':
                    resultaat = l * r
                elif node.op == '/':
                    if r == 0:
                        return BinaryOpNode(node.op, left, right)
                    resultaat = l // r if (left.type_name == 'int' and right.type_name == 'int') else l / r
                elif node.op == '%':
                    if r == 0:
                        return BinaryOpNode(node.op, left, right)
                    resultaat = l % r
                elif node.op == '==':
                    resultaat = int(l == r)
                elif node.op == '!=':
                    resultaat = int(l != r)
                elif node.op == '<':
                    resultaat = int(l < r)
                elif node.op == '>':
                    resultaat = int(l > r)
                elif node.op == '<=':
                    resultaat = int(l <= r)
                elif node.op == '>=':
                    resultaat = int(l >= r)
                elif node.op == '&&':
                    resultaat = int(bool(l) and bool(r))
                elif node.op == '||':
                    resultaat = int(bool(l) or bool(r))
                elif node.op == '&':
                    resultaat = l & r
                elif node.op == '|':
                    resultaat = l | r
                elif node.op == '^':
                    resultaat = l ^ r
                elif node.op == '<<':
                    resultaat = l << r
                elif node.op == '>>':
                    resultaat = l >> r
                else:
                    return BinaryOpNode(node.op, left, right)
            except Exception:
                return BinaryOpNode(node.op, left, right)

            result_type = 'float' if (left.type_name == 'float' or right.type_name == 'float') else 'int'
            return LiteralNode(resultaat, result_type)

        return BinaryOpNode(node.op, left, right)

    def visitUnaryOp(self, node):
        operand = node.operand.accept(self)

        # ++ en -- hebben side effects → niet folden, wel known_values invalideren
        if node.op in ('prefix++', 'prefix--', 'suffix++', 'suffix--'):
            if isinstance(node.operand, VariableNode):
                self.known_values.pop(node.operand.name, None)
            return UnaryOpNode(node.op, node.operand)

        if isinstance(operand, LiteralNode):
            v = operand.value
            try:
                if node.op == '-':
                    return LiteralNode(-v, operand.type_name)
                elif node.op == '+':
                    return LiteralNode(+v, operand.type_name)
                elif node.op == '!':
                    return LiteralNode(int(not bool(v)), 'int')
                elif node.op == '~':
                    return LiteralNode(~v, operand.type_name)
                elif node.op == '&':
                    # address-of: gebruik originele operand, niet de gepropageerde waarde
                    return UnaryOpNode('&', node.operand)
                elif node.op == '*':
                    return UnaryOpNode('*', operand)
            except Exception:
                pass

        return UnaryOpNode(node.op, operand)

    def visitCast(self, node):
        operand = node.operand.accept(self)

        if isinstance(operand, LiteralNode):
            target = node.target_type.base_type
            try:
                if target == 'int':
                    return LiteralNode(int(operand.value), 'int')
                elif target == 'float':
                    return LiteralNode(float(operand.value), 'float')
                elif target == 'char':
                    return LiteralNode(chr(int(operand.value)), 'char')
            except Exception:
                pass

        return CastNode(node.target_type, operand)

    def visitType(self, node):
        return node