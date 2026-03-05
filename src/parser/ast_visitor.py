# src/parser/ast_visitor.py

from antlr4 import ParseTreeVisitor
from .ast_nodes import (
    LiteralNode, BinaryOpNode, UnaryOpNode,
    VariableNode, VarDeclNode, AssignNode,
    CastNode, TypeNode, BlockNode, ProgramNode
)


class CSTtoASTVisitor(ParseTreeVisitor):
    """
    Zet de ANTLR Concrete Syntax Tree (CST) om naar onze eigen AST.

    Elke methode hier komt overeen met één grammar regel.
    De naamconventie is altijd: visit + (naam van de grammar regel met hoofdletter).
    Dus grammar regel 'program' → visitProgram(), 'varDec' → visitVarDec(), enz.
    """

    # --------------------------------------------------------
    # visitProgram: de startegel van de grammar
    # --------------------------------------------------------
    # Grammar: program : INT_KW MAIN LPAREN RPAREN block EOF
    #
    # De CST ziet er zo uit:
    #   program
    #     ├── 'int'
    #     ├── 'main'
    #     ├── '('
    #     ├── ')'
    #     ├── block       ← het enige kind dat we nodig hebben
    #     └── EOF
    #
    # We hoeven alleen de block te bezoeken en die in een ProgramNode te stoppen.
    def visitProgram(self, ctx):
        # ctx.block() geeft de block context terug
        block = self.visit(ctx.block())
        return ProgramNode(block)

    # --------------------------------------------------------
    # visitBlock: een blok van statements
    # --------------------------------------------------------
    # Grammar: block : LBRACE (statement)* RBRACE
    #
    # ctx.statement() geeft een lijst van alle statement-contexten.
    # We bezoeken elk statement en verzamelen de resultaten in een lijst.
    def visitBlock(self, ctx):
        statements = []
        for stmt_ctx in ctx.statement():
            stmt = self.visit(stmt_ctx)
            statements.append(stmt)
        return BlockNode(statements)

    # --------------------------------------------------------
    # visitStatement: één statement
    # --------------------------------------------------------
    # Grammar:
    #   statement : varDec
    #             | expression SC
    #             | varAss
    #
    # ANTLR maakt automatisch één van de drie alternatieven.
    # We bezoeken gewoon het eerste (en enige) relevante kind.
    #
    # ctx.varDec()   → niet None als het een varDec is
    # ctx.varAss()   → niet None als het een varAss is
    # ctx.expression → niet None als het een expressie is
    def visitStatement(self, ctx):
        if ctx.varDec():
            return self.visit(ctx.varDec())

        if ctx.varAss():
            return self.visit(ctx.varAss())

        # anders: expression SC → we gooien de ';' weg en bezoeken de expressie
        # ANTLR genereert ctx.expression() ZONDER index als expression maar
        # één keer voorkomt in deze grammar regel.
        # ctx.expression(i) met index werkt alleen als het meerdere keren voorkomt
        # (zoals in varAss: expression ASSIGN expression)
        return self.visit(ctx.expression())

    # --------------------------------------------------------
    # visitType: een type zoals int, const float*, int**
    # --------------------------------------------------------
    # Grammar: type : CONST_KW? baseType STAR*
    #
    # We kijken:
    #   1. Is er een CONST_KW token? Dan is_const = True
    #   2. Wat is het basistype? (baseType regel)
    #   3. Hoeveel STAR tokens zijn er? Dat is de pointer_depth
    def visitType(self, ctx):
        # 1. is er een 'const' keyword?
        # ctx.CONST_KW() geeft het token terug, of None als het er niet is
        is_const = ctx.CONST_KW() is not None

        # 2. bezoek de baseType regel om de string te krijgen ('int', 'float', 'char')
        base_type = self.visit(ctx.baseType())

        # 3. tel het aantal sterretjes
        # ctx.STAR() geeft een LIJST van alle STAR tokens terug
        pointer_depth = len(ctx.STAR())

        return TypeNode(base_type, pointer_depth, is_const)

    # --------------------------------------------------------
    # visitBaseType: het basistype keyword
    # --------------------------------------------------------
    # Grammar: baseType : INT_KW | FLOAT_KW | CHAR_KW
    #
    # We geven gewoon de tekst terug als string: 'int', 'float' of 'char'
    def visitBaseType(self, ctx):
        return ctx.getText()

    # --------------------------------------------------------
    # visitVarDec: variabele declaratie
    # --------------------------------------------------------
    # Grammar: varDec : type ID (ASSIGN expression)? SC
    #
    # Voorbeelden:
    #   int x;              → VarDeclNode(TypeNode('int'), 'x', None)
    #   float y = 3.14;     → VarDeclNode(TypeNode('float'), 'y', LiteralNode(3.14))
    #   const int* p = &z;  → VarDeclNode(TypeNode('int',1,True), 'p', UnaryOpNode('&',...))
    def visitVarDec(self, ctx):
        # bezoek de type regel → TypeNode
        var_type = self.visit(ctx.type_())

        # haal de naam van de variabele op als string
        # ctx.ID() geeft het ID token, .getText() geeft de tekst ervan
        name = ctx.ID().getText()

        # is er een initialisatiewaarde?
        # ctx.expression() geeft een lijst terug → [] als er geen is, [ctx] als er wel een is
        # MAAR: omdat expression maar één keer voorkomt in varDec, genereert ANTLR
        # ctx.expression() ZONDER index → geeft een enkel object terug, of None
        if ctx.expression():
            value = self.visit(ctx.expression())
        else:
            value = None

        return VarDeclNode(var_type, name, value)

    # --------------------------------------------------------
    # visitVarAss: assignment statement
    # --------------------------------------------------------
    # Grammar: varAss : expression ASSIGN expression SC
    #
    # De linkerkant is een expressie (lvalue):
    #   x = 5;       → AssignNode(VariableNode('x'), LiteralNode(5))
    #   *ptr = 3;    → AssignNode(UnaryOpNode('*', VariableNode('ptr')), LiteralNode(3))
    #
    # ctx.expression() geeft een LIJST van de twee expressies terug:
    #   [0] = linkerkant (target)
    #   [1] = rechterkant (waarde)
    def visitVarAss(self, ctx):
        target = self.visit(ctx.expression(0))
        value  = self.visit(ctx.expression(1))
        return AssignNode(target, value)

    # --------------------------------------------------------
    # visitExpression: het hart van de visitor
    # --------------------------------------------------------
    # Grammar heeft veel alternatieven. We bekijken de structuur
    # van de CST om te beslissen welk geval het is.
    #
    # Strategie:
    #   - Hoeveel kinderen heeft de node?
    #   - Wat is het eerste/laatste token?
    #   - Is er een type-kind? (dan is het een cast)
    def visitExpression(self, ctx):
        child_count = ctx.getChildCount()

        # ── GEVAL 1: INTEGER literal ────────────────────────
        # Voorbeeld: 42
        # Structuur: één kind, namelijk het INTEGER token
        if ctx.INTEGER():
            waarde = int(ctx.INTEGER().getText())
            return LiteralNode(waarde, 'int')

        # ── GEVAL 2: FLOAT literal ──────────────────────────
        # Voorbeeld: 3.14
        if ctx.FLOAT():
            waarde = float(ctx.FLOAT().getText())
            return LiteralNode(waarde, 'float')

        # ── GEVAL 3: CHAR literal ───────────────────────────
        # Voorbeeld: 'a'
        # ctx.CHAR().getText() geeft "'a'" terug (met aanhalingstekens)
        # We halen het middelste karakter eruit
        if ctx.CHAR():
            tekst = ctx.CHAR().getText()  # bv. "'a'"
            # verwijder de aanhalingstekens: "'a'" → "a"
            # maar let op escape sequences zoals '\n'
            inner = tekst[1:-1]  # alles tussen de quotes
            if inner.startswith('\\'):
                # escape sequence: '\n' → newline, '\t' → tab, enz.
                escape_map = {
                    'n': '\n', 't': '\t', 'r': '\r',
                    'b': '\b', 'f': '\f', '\\': '\\', "'": "'"
                }
                waarde = escape_map.get(inner[1], inner[1])
            else:
                waarde = inner
            return LiteralNode(waarde, 'char')

        # ── GEVAL 4: variabele (identifier) ────────────────
        # Voorbeeld: x, my_var
        if ctx.ID():
            return VariableNode(ctx.ID().getText())

        # ── GEVAL 5: cast → (type) expression ──────────────
        # Voorbeeld: (int) x, (float*) ptr
        # Structuur: LPAREN type RPAREN expression
        # We herkennen dit doordat er een type()-kind is
        if ctx.type_():
            target_type = self.visit(ctx.type_())
            operand = self.visit(ctx.expression(0))
            return CastNode(target_type, operand)

        # ── GEVAL 6: haakjes → ( expression ) ──────────────
        # Voorbeeld: (3 + 4)
        # Structuur: LPAREN expression RPAREN
        # 3 kinderen, eerste is '('
        if child_count == 3 and ctx.getChild(0).getText() == '(':
            return self.visit(ctx.expression(0))

        # ── GEVAL 7: alle unaire operatoren (prefix én suffix) ──
        # Dit blok handelt ALLE gevallen af met 2 kinderen.
        # We onderscheiden prefix en suffix door te kijken welk kind de operator is:
        #
        #   suffix: expression OP  → kind 0 is expressie, kind 1 is operator
        #     bv. x++  → kind 0 = expression(x), kind 1 = '++'
        #
        #   prefix: OP expression  → kind 0 is operator, kind 1 is expressie
        #     bv. ++x  → kind 0 = '++', kind 1 = expression(x)
        #     bv. -3   → kind 0 = '-',  kind 1 = expression(3)
        #     bv. &x   → kind 0 = '&',  kind 1 = expression(x)
        #     bv. *ptr → kind 0 = '*',  kind 1 = expression(ptr)
        if child_count == 2:
            first = ctx.getChild(0).getText()
            last  = ctx.getChild(1).getText()

            # suffix ++/-- : het LAATSTE kind is de operator
            if last == '++':
                return UnaryOpNode('suffix++', self.visit(ctx.expression(0)))
            if last == '--':
                return UnaryOpNode('suffix--', self.visit(ctx.expression(0)))

            # prefix ++/-- : het EERSTE kind is de operator
            # aparte namen zodat code generation later het verschil ziet
            if first == '++':
                return UnaryOpNode('prefix++', self.visit(ctx.expression(0)))
            if first == '--':
                return UnaryOpNode('prefix--', self.visit(ctx.expression(0)))

            # alle andere unaire prefix operatoren: -, +, !, ~, &, *
            return UnaryOpNode(first, self.visit(ctx.expression(0)))

        # ── GEVAL 8: binaire operatie ────────────────────────
        # Voorbeeld: 3 + 4, x * y, a && b
        # Structuur: expression OPERATOR expression
        # 3 kinderen
        if child_count == 3:
            left     = self.visit(ctx.expression(0))
            operator = ctx.getChild(1).getText()
            right    = self.visit(ctx.expression(1))
            return BinaryOpNode(operator, left, right)

        # ── GEVAL 9: onverwacht ─────────────────────────────
        raise ValueError(
            f"Onverwacht patroon in expression: {ctx.getText()!r} "
            f"(aantal kinderen: {child_count})"
        )