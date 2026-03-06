# src/parser/ast_visitor.py

from antlr4 import ParseTreeVisitor
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


class CSTtoASTVisitor(ParseTreeVisitor):
    """
    Zet de ANTLR Concrete Syntax Tree (CST) om naar onze eigen AST.

    Elke methode hier komt overeen met één grammar regel.
    Naamconventie: visit + (naam van de grammar regel met hoofdletter).

    Assignment 4 voegt toe:
      - visitProgram     : leest nu ook de enumDef* kinderen vóór main
      - visitStatement   : herkent if, while, for, break, continue, switch, scope
      - visitEnumDef     : enum definitie → EnumDefNode
      - visitIfStmt      : if/else/else-if → IfNode
      - visitWhileStmt   : while → WhileNode
      - visitForStmt     : for → VarDecl/Assign + WhileNode (vertaling!)
      - visitBreakStmt   : break → BreakNode
      - visitContinueStmt: continue → ContinueNode
      - visitSwitchStmt  : switch → IfNode keten (vertaling!)
      - visitScopeStmt   : anonieme scope → ScopeNode
      - visitType        : uitgebreid met enum type
    """

    def __init__(self):
        self.errors = []

    # --------------------------------------------------------
    # visitProgram
    # --------------------------------------------------------
    # Grammar: program : (includeStmt | comment | enumDef)* INT_KW MAIN ... block EOF
    #
    # NIEUW in assignment 4: enumDef* kinderen vóór main worden verzameld
    # en apart opgeslagen in ProgramNode.enums.
    #
    # EDGE CASE: ctx.enumDef() geeft een lege lijst als er geen enums zijn.
    # EDGE CASE: de volgorde van includes/comments/enums in de broncode
    # is niet relevant voor de compiler — we bewaren ze apart per type.
    def visitProgram(self, ctx):
        # verzamel includes
        includes = []
        for inc_ctx in ctx.includeStmt():
            includes.append(self.visit(inc_ctx))

        # verzamel top-level comments
        top_comments = []
        for cmt_ctx in ctx.comment():
            top_comments.append(self.visit(cmt_ctx))

        # NIEUW: verzamel enum definities
        enums = []
        for enum_ctx in ctx.enumDef():
            enums.append(self.visit(enum_ctx))

        # bezoek de block (body van main)
        block = self.visit(ctx.block())

        # top-level comments aan het begin van de block statements
        if top_comments:
            block.statements = top_comments + block.statements

        return ProgramNode(block, includes, enums)

    # --------------------------------------------------------
    # visitEnumDef (NIEUW)
    # --------------------------------------------------------
    # Grammar: enumDef : ENUM_KW ID LBRACE ID (COMMA ID)* RBRACE SC
    #
    # De eerste ID is de naam van de enum (bv. 'Status').
    # Alle overige IDs zijn de labels (bv. ['READY', 'BUSY', 'OFFLINE']).
    #
    # EDGE CASE: ctx.ID() geeft een LIJST van alle ID-tokens terug.
    # Het EERSTE element is de enum naam, de REST zijn de labels.
    def visitEnumDef(self, ctx):
        all_ids = ctx.ID()                      # lijst van alle ID tokens
        name    = all_ids[0].getText()          # eerste ID = enum naam
        labels  = [id_.getText() for id_ in all_ids[1:]]  # rest = labels
        return EnumDefNode(name, labels)

    # --------------------------------------------------------
    # visitIncludeStmt (ongewijzigd van assignment 3)
    # --------------------------------------------------------
    def visitIncludeStmt(self, ctx):
        token_text = ctx.INCLUDE_STDIO().getText()
        start  = token_text.index('<') + 1
        end    = token_text.index('>')
        header = token_text[start:end]
        return IncludeNode(header)

    # --------------------------------------------------------
    # visitBlock (ongewijzigd)
    # --------------------------------------------------------
    def visitBlock(self, ctx):
        statements = []
        for stmt_ctx in ctx.statement():
            stmt = self.visit(stmt_ctx)
            statements.append(stmt)
        return BlockNode(statements)

    # --------------------------------------------------------
    # visitStatement (uitgebreid)
    # --------------------------------------------------------
    # Grammar:
    #   statement : varDec | arrayDec | varAss | functionCall SC
    #             | expression SC | comment
    #             | ifStmt | whileStmt | forStmt        ← NIEUW
    #             | breakStmt | continueStmt            ← NIEUW
    #             | switchStmt | scopeStmt              ← NIEUW
    #
    # VOLGORDE: control flow checks komen NA de bestaande checks.
    # De nieuwe alternatieven beginnen elk met een uniek keyword dus
    # er is geen ambiguïteit met de bestaande regels.
    def visitStatement(self, ctx):
        if ctx.varDec():
            return self.visit(ctx.varDec())
        if ctx.arrayDec():
            return self.visit(ctx.arrayDec())
        if ctx.varAss():
            return self.visit(ctx.varAss())
        if ctx.functionCall():
            return self.visit(ctx.functionCall())
        if ctx.comment():
            return self.visit(ctx.comment())

        # NIEUW: control flow
        if ctx.ifStmt():
            return self.visit(ctx.ifStmt())
        if ctx.whileStmt():
            return self.visit(ctx.whileStmt())
        if ctx.forStmt():
            return self.visit(ctx.forStmt())
        if ctx.breakStmt():
            return self.visit(ctx.breakStmt())
        if ctx.continueStmt():
            return self.visit(ctx.continueStmt())
        if ctx.switchStmt():
            return self.visit(ctx.switchStmt())
        if ctx.scopeStmt():
            return self.visit(ctx.scopeStmt())

        # fallback: expression SC
        return self.visit(ctx.expression())

    # --------------------------------------------------------
    # visitIfStmt (NIEUW)
    # --------------------------------------------------------
    # Grammar: ifStmt : IF_KW LPAREN expression RPAREN block
    #                   (ELSE_KW (block | ifStmt))?
    #
    # Drie gevallen:
    #   1. if (cond) { ... }                     → else_block = None
    #   2. if (cond) { ... } else { ... }        → else_block = BlockNode
    #   3. if (cond) { ... } else if (...) { }   → else_block = IfNode (recursief)
    #
    # ANTLR geeft de else-tak terug via ctx.block() en ctx.ifStmt():
    #   - ctx.block()  geeft een LIJST: [then_block] of [then_block, else_block]
    #   - ctx.ifStmt() geeft de geneste if terug als er een 'else if' is
    #
    # EDGE CASE: ctx.block() heeft altijd minstens één element (de then-tak).
    # Een tweede element is aanwezig als de else-tak een block is.
    def visitIfStmt(self, ctx):
        condition  = self.visit(ctx.expression())
        then_block = self.visit(ctx.block(0))   # altijd aanwezig

        else_block = None
        if ctx.ELSE_KW():
            if ctx.ifStmt():
                # else if → recursief IfNode
                else_block = self.visit(ctx.ifStmt())
            else:
                # gewone else → tweede block
                else_block = self.visit(ctx.block(1))

        return IfNode(condition, then_block, else_block)

    # --------------------------------------------------------
    # visitWhileStmt (NIEUW)
    # --------------------------------------------------------
    # Grammar: whileStmt : WHILE_KW LPAREN expression RPAREN block
    #
    # Eenvoudig: conditie + body, geen update.
    def visitWhileStmt(self, ctx):
        condition = self.visit(ctx.expression())
        body      = self.visit(ctx.block())
        return WhileNode(condition, body, update=None)

    # --------------------------------------------------------
    # visitForStmt (NIEUW) — vertaling naar WhileNode
    # --------------------------------------------------------
    # Grammar: forStmt : FOR_KW LPAREN forInit? SC expression? SC expression? RPAREN block
    #
    # Een for-lus wordt in de AST OMGEZET naar een structuur die de LLVM
    # visitor makkelijk kan verwerken. We geven een LIJST van statements terug
    # in plaats van één node, zodat de init vóór de while kan staan.
    #
    # MAAR: visitStatement verwacht één node terug. Oplossing: we geven een
    # speciaal ForUnpackNode terug... of we pakken dit anders aan.
    #
    # BETERE AANPAK: we geven een BlockNode terug die de init + while bevat.
    # De caller (visitStatement) zet dit gewoon in de statement lijst.
    # De omringende visitBlock zal dit zien als één statement (een BlockNode),
    # wat semantisch correct is — de for-lus heeft zijn eigen scope.
    #
    # Structuur van de vertaling:
    #   for (init; cond; update) { body }
    #   →  ScopeNode(BlockNode([
    #          init_stmt,          ← VarDeclNode of AssignNode (of niets)
    #          WhileNode(
    #            condition = cond  ← of LiteralNode(1) als leeg
    #            body      = BlockNode([body..., update_as_stmt])
    #            update    = update_expr  ← voor continue-correctheid
    #          )
    #      ]))
    #
    # EDGE CASE: lege init (for(; cond; update)) → geen init_stmt
    # EDGE CASE: lege conditie (for(init;;)) → condition = LiteralNode(1, 'int')
    # EDGE CASE: lege update (for(init; cond;)) → geen update in body
    # EDGE CASE: continue in for-lus → WhileNode.update zodat LLVM visitor
    #            weet dat update uitgevoerd moet worden vóór de volgende iteratie
    def visitForStmt(self, ctx):
        # ── INIT ──────────────────────────────────────────────────────────
        # forInit? → kan None zijn
        init_stmt = None
        if ctx.forInit():
            init_stmt = self.visit(ctx.forInit())

        # ── CONDITIE ──────────────────────────────────────────────────────
        # expression? op positie 0 (na de eerste ';')
        # ctx.expression() geeft een lijst: [cond] of [cond, update] of []
        expressions = ctx.expression()

        if len(expressions) >= 1:
            condition = self.visit(expressions[0])
        else:
            # lege conditie → altijd waar (oneindige lus)
            condition = LiteralNode(1, 'int')

        # ── UPDATE ────────────────────────────────────────────────────────
        # expression? op positie 1 (na de tweede ';')
        update_expr = None
        if len(expressions) >= 2:
            update_expr = self.visit(expressions[1])

        # ── BODY ──────────────────────────────────────────────────────────
        body_block = self.visit(ctx.block())

        # voeg de update toe als LAATSTE statement in de body
        # zodat hij bij elke iteratie uitgevoerd wordt
        # (continue in de LLVM visitor springt naar het update-label)
        if update_expr is not None:
            # wrap de update expressie als statement
            body_block.statements = body_block.statements + [update_expr]

        # bouw de WhileNode — update opslaan voor continue-correctheid
        while_node = WhileNode(condition, body_block, update=update_expr)

        # wrap alles in een ScopeNode zodat de init-variabele scoped is
        inner_stmts = []
        if init_stmt is not None:
            inner_stmts.append(init_stmt)
        inner_stmts.append(while_node)

        return ScopeNode(BlockNode(inner_stmts))

    # --------------------------------------------------------
    # visitForInit (NIEUW)
    # --------------------------------------------------------
    # Grammar: forInit : type ID (ASSIGN expression)?   (declaratie)
    #                  | expression                      (expressie)
    #
    # EDGE CASE: onderscheid tussen declaratie en expressie:
    #   - ctx.type_() aanwezig → declaratie (int i = 0)
    #   - anders → expressie (i = 0, i++)
    def visitForInit(self, ctx):
        if ctx.type_():
            # declaratie: int i = 0
            var_type = self.visit(ctx.type_())
            name     = ctx.ID().getText()
            value    = self.visit(ctx.expression()) if ctx.expression() else None
            return VarDeclNode(var_type, name, value)
        else:
            # expressie: i = 0 of i++
            return self.visit(ctx.expression())

    # --------------------------------------------------------
    # visitBreakStmt / visitContinueStmt (NIEUW)
    # --------------------------------------------------------
    # Grammar: breakStmt    : BREAK_KW SC
    #          continueStmt : CONTINUE_KW SC
    #
    # Beide zijn blad-nodes zonder kinderen.
    def visitBreakStmt(self, ctx):
        return BreakNode()

    def visitContinueStmt(self, ctx):
        return ContinueNode()

    # --------------------------------------------------------
    # visitSwitchStmt (NIEUW) — vertaling naar IfNode keten
    # --------------------------------------------------------
    # Grammar: switchStmt : SWITCH_KW LPAREN expression RPAREN
    #                       LBRACE caseClause* defaultClause? RBRACE
    #
    # Een switch wordt omgezet naar een if-else keten:
    #   switch (x) {
    #     case 1: stmts1 break;
    #     case 2: stmts2 break;
    #     default: stmts3
    #   }
    # →
    #   if (x == 1) { stmts1 }
    #   else if (x == 2) { stmts2 }
    #   else { stmts3 }
    #
    # EDGE CASE: geen cases → geef een lege ScopeNode terug
    # EDGE CASE: geen default → de else-tak van de laatste if is None
    # EDGE CASE: break aan het einde van een case → wordt WEGGEGOOID
    #   in de vertaling, want de if-else structuur heeft geen fallthrough.
    #   Een break buiten de case-body (bv. in een geneste while) blijft wel.
    # EDGE CASE: lege case body → BlockNode([])
    #
    # BELANGRIJK: de switch-expressie (x) kan side-effects hebben (bv. x++).
    # We evalueren hem maar één keer door hem op te slaan in een tijdelijke
    # variabele. Dit doen we NIET in de AST (te complex) — we vertrouwen
    # erop dat de expressie geen side-effects heeft in onze subset van C.
    def visitSwitchStmt(self, ctx):
        switch_expr = self.visit(ctx.expression())

        # check voor directe varDecl in switch zonder anonieme scope
        for case_ctx in ctx.caseClause():
            for stmt_ctx in case_ctx.statement():
                if stmt_ctx.varDec() or stmt_ctx.arrayDec():
                    self.errors.append(
                        "[ Error ] Variabele declaratie direct in switch body "
                        "zonder anonieme scope. Gebruik { } om een scope te maken."
                    )
        if ctx.defaultClause():
            for stmt_ctx in ctx.defaultClause().statement():
                if stmt_ctx.varDec() or stmt_ctx.arrayDec():
                    self.errors.append(
                        "[ Error ] Variabele declaratie direct in switch body "
                        "zonder anonieme scope. Gebruik { } om een scope te maken."
                    )

        # check voor meerdere case-labels op één body
        case_ctxs = ctx.caseClause()
        for idx, case_ctx in enumerate(case_ctxs):
            if len(case_ctx.statement()) == 0 and idx < len(case_ctxs) - 1:
                self.errors.append(
                    "[ Error ] Meerdere case-labels op één body zijn niet ondersteund. "
                    "Elke case moet zijn eigen body hebben."
                )

        # verzamel alle case-clauses
        cases = []
        for case_ctx in ctx.caseClause():
            cases.append(self.visit(case_ctx))

        # verzamel de default-clause (optioneel)
        default_stmts = None
        if ctx.defaultClause():
            default_stmts = self.visit(ctx.defaultClause())

        # geen cases en geen default → lege scope
        if not cases and default_stmts is None:
            return ScopeNode(BlockNode([]))

        # bouw de if-else keten van achter naar voren
        current_else = None
        if default_stmts is not None:
            current_else = BlockNode(default_stmts)

        for case_value_expr, case_stmts in reversed(cases):
            condition = BinaryOpNode('==', switch_expr, case_value_expr)
            then_block = BlockNode(case_stmts)
            current_else = IfNode(condition, then_block, current_else)

        return current_else

    # --------------------------------------------------------
    # visitCaseClause (NIEUW)
    # --------------------------------------------------------
    # Grammar: caseClause : CASE_KW expression COLON statement*
    #
    # Geeft een tuple terug: (waarde_expressie, lijst_van_statements)
    # Break-statements AAN HET EINDE van de case worden weggegoid
    # (want de if-else vertaling heeft geen fallthrough).
    #
    # EDGE CASE: break middenin een case (bv. in een geneste while) blijft wél,
    # want die break behoort niet tot de switch-case logica maar tot de while.
    # We verwijderen alleen de LAATSTE statement als het een BreakNode is.
    def visitCaseClause(self, ctx):
        value_expr = self.visit(ctx.expression())
        stmts = []
        for stmt_ctx in ctx.statement():
            stmts.append(self.visit(stmt_ctx))

        # break direct als laatste statement
        if stmts and isinstance(stmts[-1], BreakNode):
            stmts.pop()
        # break als laatste statement IN een anonieme scope
        elif stmts and isinstance(stmts[-1], ScopeNode):
            scope_stmts = stmts[-1].body.statements
            if scope_stmts and isinstance(scope_stmts[-1], BreakNode):
                scope_stmts.pop()

        return (value_expr, stmts)

    # --------------------------------------------------------
    # visitDefaultClause (NIEUW)
    # --------------------------------------------------------
    # Grammar: defaultClause : DEFAULT_KW COLON statement*
    #
    # Geeft een lijst van statements terug.
    def visitDefaultClause(self, ctx):
        stmts = []
        for stmt_ctx in ctx.statement():
            stmts.append(self.visit(stmt_ctx))

        # break direct als laatste statement
        if stmts and isinstance(stmts[-1], BreakNode):
            stmts.pop()
        # break als laatste statement IN een anonieme scope
        elif stmts and isinstance(stmts[-1], ScopeNode):
            scope_stmts = stmts[-1].body.statements
            if scope_stmts and isinstance(scope_stmts[-1], BreakNode):
                scope_stmts.pop()

        return stmts

    # --------------------------------------------------------
    # visitScopeStmt (NIEUW)
    # --------------------------------------------------------
    # Grammar: scopeStmt : block
    #
    # Een anonieme scope is gewoon een block als statement.
    def visitScopeStmt(self, ctx):
        body = self.visit(ctx.block())
        return ScopeNode(body)

    # --------------------------------------------------------
    # visitType (uitgebreid voor enum types)
    # --------------------------------------------------------
    # Grammar: type : CONST_KW? baseType STAR*
    #               | ENUM_KW ID
    #
    # NIEUW: tweede alternatief voor enum types.
    # ANTLR onderscheidt de twee alternatieven via ctx.ENUM_KW():
    #   - ctx.ENUM_KW() aanwezig → enum type: TypeNode('EnumNaam', 0, False)
    #   - anders → bestaand gedrag (baseType + const + pointers)
    #
    # EDGE CASE: een enum type heeft geen pointer depth en geen const
    # in onze subset van C.
    def visitType(self, ctx):
        if ctx.ENUM_KW():
            # enum type: ENUM_KW ID → TypeNode met de enum naam als base_type
            enum_name = ctx.ID().getText()
            return TypeNode(enum_name, pointer_depth=0, is_const=False)

        # bestaand gedrag (ongewijzigd van assignment 3)
        is_const      = ctx.CONST_KW() is not None
        base_type     = self.visit(ctx.baseType())
        pointer_depth = len(ctx.STAR())
        return TypeNode(base_type, pointer_depth, is_const)

    # --------------------------------------------------------
    # Hieronder: ONGEWIJZIGD van assignment 3
    # --------------------------------------------------------

    def visitBaseType(self, ctx):
        return ctx.getText()

    def visitVarDec(self, ctx):
        var_type = self.visit(ctx.type_())
        name     = ctx.ID().getText()
        if ctx.expression():
            value = self.visit(ctx.expression())
        else:
            value = None
        return VarDeclNode(var_type, name, value)

    def visitVarAss(self, ctx):
        target = self.visit(ctx.expression(0))
        value  = self.visit(ctx.expression(1))
        return AssignNode(target, value)

    def visitArrayDec(self, ctx):
        var_type   = self.visit(ctx.type_())
        name       = ctx.ID().getText()
        dimensions = [int(tok.getText()) for tok in ctx.INTEGER()]
        initializer = None
        if ctx.arrayInit():
            initializer = self.visit(ctx.arrayInit())
        return ArrayDeclNode(var_type, name, dimensions, initializer)

    def visitArrayInit(self, ctx):
        elements = []
        for elem_ctx in ctx.arrayElement():
            elements.append(self.visit(elem_ctx))
        return ArrayInitNode(elements)

    def visitArrayElement(self, ctx):
        if ctx.arrayInit():
            return self.visit(ctx.arrayInit())
        return self.visit(ctx.expression())

    def visitFunctionCall(self, ctx):
        name = ctx.ID().getText()
        args = [self.visit(e) for e in ctx.expression()]
        return FunctionCallNode(name, args)

    def visitComment(self, ctx):
        if ctx.LINE_COMMENT_TOKEN():
            text = ctx.LINE_COMMENT_TOKEN().getText()
        else:
            text = ctx.BLOCK_COMMENT_TOKEN().getText()
        return CommentNode(text)

    def visitExpression(self, ctx):
        child_count = ctx.getChildCount()

        if ctx.INTEGER():
            return LiteralNode(int(ctx.INTEGER().getText()), 'int')

        if ctx.FLOAT():
            return LiteralNode(float(ctx.FLOAT().getText()), 'float')

        if ctx.CHAR():
            tekst = ctx.CHAR().getText()
            inner = tekst[1:-1]
            if inner.startswith('\\'):
                escape_map = {
                    'n': '\n', 't': '\t', 'r': '\r',
                    'b': '\b', 'f': '\f', '\\': '\\', "'": "'"
                }
                waarde = escape_map.get(inner[1], inner[1])
            else:
                waarde = inner
            return LiteralNode(waarde, 'char')

        if ctx.STRING():
            raw   = ctx.STRING().getText()
            value = raw[1:-1]
            return StringLiteralNode(value)

        if ctx.ID():
            return VariableNode(ctx.ID().getText())

        if ctx.functionCall():
            return self.visit(ctx.functionCall())

        # cast: LPAREN type RPAREN expression → type() aanwezig
        if ctx.type_():
            target_type = self.visit(ctx.type_())
            operand     = self.visit(ctx.expression(0))
            return CastNode(target_type, operand)

        # suffix ++ of --: expression PLUSPLUS / MINUSMINUS (2 kinderen)
        if child_count == 2:
            child1 = ctx.getChild(1).getText()
            if child1 == '++':
                return UnaryOpNode('suffix++', self.visit(ctx.expression(0)))
            if child1 == '--':
                return UnaryOpNode('suffix--', self.visit(ctx.expression(0)))

        # unaire operatoren (prefix): -, +, !, ~, &, *, ++, --
        if child_count == 2:
            op_text = ctx.getChild(0).getText()
            operand = self.visit(ctx.expression(0))
            return UnaryOpNode(op_text, operand)

        # haakjes: ( expression ) → 3 kinderen: '(' expr ')'
        if child_count == 3 and ctx.getChild(0).getText() == '(':
            return self.visit(ctx.expression(0))

        # array toegang: expression '[' expression ']' → 4 kinderen
        if child_count == 4 and ctx.getChild(1).getText() == '[':
            array_expr = self.visit(ctx.expression(0))
            index      = self.visit(ctx.expression(1))
            return ArrayAccessNode(array_expr, index)

        # binaire operatie: expression op expression → 3 kinderen
        if child_count == 3:
            left  = self.visit(ctx.expression(0))
            op    = ctx.getChild(1).getText()
            right = self.visit(ctx.expression(1))
            return BinaryOpNode(op, left, right)

        # fallback (zou niet mogen voorkomen na semantic analysis)
        return LiteralNode(0, 'int')