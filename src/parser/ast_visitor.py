# src/parser/ast_visitor.py

from antlr4 import ParseTreeVisitor
from .ast_nodes import (
    LiteralNode, BinaryOpNode, UnaryOpNode,
    VariableNode, VarDeclNode, AssignNode,
    CastNode, TypeNode, BlockNode, ProgramNode,
    # Nieuw in assignment 3:
    CommentNode, ArrayDeclNode, ArrayInitNode,
    ArrayAccessNode, StringLiteralNode,
    FunctionCallNode, IncludeNode
)


class CSTtoASTVisitor(ParseTreeVisitor):
    """
    Zet de ANTLR Concrete Syntax Tree (CST) om naar onze eigen AST.

    Elke methode hier komt overeen met één grammar regel.
    Naamconventie: visit + (naam van de grammar regel met hoofdletter).

    Assignment 3 voegt toe:
      - visitProgram     : leest nu ook de includeStmt* kinderen
      - visitStatement   : herkent arrayDec, functionCall SC, comment
      - visitIncludeStmt : #include <stdio.h> → IncludeNode
      - visitArrayDec    : array declaratie → ArrayDeclNode
      - visitArrayInit   : { ... } → ArrayInitNode
      - visitArrayElement: expressie of geneste { ... }
      - visitFunctionCall: printf(...) → FunctionCallNode
      - visitComment     : // of /* */ → CommentNode
      - visitExpression  : uitgebreid met array toegang, STRING, functionCall
    """

    # --------------------------------------------------------
    # visitProgram: de startegel van de grammar
    # --------------------------------------------------------
    # Grammar: program : (includeStmt | comment)* INT_KW MAIN LPAREN RPAREN block EOF
    #
    # We itereren over alle kinderen vóór 'int' om includes én comments
    # te verzamelen. ctx.includeStmt() en ctx.comment() geven lijsten terug
    # van elk type apart — maar de VOLGORDE gaat verloren als we ze apart
    # itereren.
    #
    # KEUZE: we bewaren includes apart (voor stdio check) en top-level
    # comments apart. Volgorde maakt voor de compiler niet uit.
    #
    # EDGE CASE: ctx.includeStmt() geeft een lege lijst als er geen includes zijn.
    # ctx.comment() geeft een lege lijst als er geen top-level comments zijn.
    def visitProgram(self, ctx):
        # verzamel alle include nodes
        includes = []
        for inc_ctx in ctx.includeStmt():
            includes.append(self.visit(inc_ctx))

        # verzamel top-level comments (vóór int main)
        # die worden ook als statements in de body gezet zodat de
        # LLVM visitor ze kan verwerken
        top_comments = []
        for cmt_ctx in ctx.comment():
            top_comments.append(self.visit(cmt_ctx))

        # bezoek de block (de body van main)
        block = self.visit(ctx.block())

        # voeg top-level comments toe aan het begin van de block statements
        # zodat ze zichtbaar zijn in de AST en later in LLVM output
        if top_comments:
            block.statements = top_comments + block.statements

        return ProgramNode(block, includes)

    # --------------------------------------------------------
    # visitIncludeStmt: #include <stdio.h>
    # --------------------------------------------------------
    # Grammar: includeStmt : INCLUDE_STDIO
    #
    # Het INCLUDE_STDIO token matcht de hele tekst '#include <stdio.h>'.
    # We extraheren de headernaam 'stdio.h' eruit voor de IncludeNode.
    #
    # EDGE CASE: we parsen de headernaam dynamisch uit de token tekst
    # zodat we later eventueel andere includes kunnen toevoegen zonder
    # de grammar te hoeven aanpassen.
    def visitIncludeStmt(self, ctx):
        # ctx.INCLUDE_STDIO() geeft het token, .getText() geeft bv. '#include <stdio.h>'
        token_text = ctx.INCLUDE_STDIO().getText()

        # extract de headernaam: alles tussen '<' en '>'
        # '#include <stdio.h>' → 'stdio.h'
        start = token_text.index('<') + 1
        end   = token_text.index('>')
        header = token_text[start:end]

        return IncludeNode(header)

    # --------------------------------------------------------
    # visitBlock: een blok van statements
    # --------------------------------------------------------
    # Grammar: block : LBRACE (statement)* RBRACE
    # Ongewijzigd van assignment 2.
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
    #             | arrayDec          ← NIEUW
    #             | varAss
    #             | functionCall SC   ← NIEUW
    #             | expression SC
    #             | comment           ← NIEUW
    #
    # ANTLR kiest het juiste alternatief — we checken welk kind aanwezig is.
    #
    # VOLGORDE VAN CHECKEN IS BELANGRIJK:
    #   1. arrayDec vóór varDec: beide beginnen met een type, maar arrayDec
    #      heeft '[' na de naam. ANTLR's lookahead handelt dit af in de grammar,
    #      maar we checken hier gewoon ctx.arrayDec() first.
    #   2. functionCall vóór expression: een functionCall IS ook een expression
    #      in de grammar. We checken ctx.functionCall() eerst zodat we de
    #      juiste visitor-methode aanroepen.
    def visitStatement(self, ctx):
        if ctx.varDec():
            return self.visit(ctx.varDec())

        if ctx.arrayDec():
            return self.visit(ctx.arrayDec())

        if ctx.varAss():
            return self.visit(ctx.varAss())

        # NIEUW: function call als statement (de ';' gooien we weg)
        if ctx.functionCall():
            return self.visit(ctx.functionCall())

        # NIEUW: comment als statement
        if ctx.comment():
            return self.visit(ctx.comment())

        # anders: expression SC — bezoek de expressie, gooi ';' weg
        return self.visit(ctx.expression())

    # --------------------------------------------------------
    # visitType, visitBaseType, visitVarDec, visitVarAss
    # --------------------------------------------------------
    # Ongewijzigd van assignment 2.

    def visitType(self, ctx):
        is_const      = ctx.CONST_KW() is not None
        base_type     = self.visit(ctx.baseType())
        pointer_depth = len(ctx.STAR())
        return TypeNode(base_type, pointer_depth, is_const)

    def visitBaseType(self, ctx):
        return ctx.getText()

    def visitVarDec(self, ctx):
        var_type = self.visit(ctx.type_())
        name     = ctx.ID().getText()

        # BELANGRIJK: ctx.expression() hier geeft een ENKELVOUDIG object terug
        # (geen lijst), omdat 'expression' maar EEN keer voorkomt in varDec:
        #   varDec : type ID (ASSIGN expression)? SC
        # Dit verschilt van visitFunctionCall waar expression meerdere keren
        # voorkomt en ctx.expression() een lijst teruggeeft!
        # Als de grammar ooit verandert → gebruik dan ctx.expression(0).
        if ctx.expression():
            value = self.visit(ctx.expression())
        else:
            value = None

        return VarDeclNode(var_type, name, value)

    def visitVarAss(self, ctx):
        target = self.visit(ctx.expression(0))
        value  = self.visit(ctx.expression(1))
        return AssignNode(target, value)

    # --------------------------------------------------------
    # visitArrayDec: array declaratie
    # --------------------------------------------------------
    # Grammar: arrayDec : type ID (LBRACKET INTEGER RBRACKET)+ (ASSIGN arrayInit)? SC
    #
    # Voorbeelden:
    #   int arr[3];                     → ArrayDeclNode(TypeNode('int'), 'arr', [3], None)
    #   float grid[2][3] = {{...},{...}}; → ArrayDeclNode(TypeNode('float'), 'grid', [2,3], ...)
    #
    # EDGE CASE: ctx.INTEGER() geeft een LIJST van alle INTEGER tokens terug,
    # één per dimensie. We itereren over de lijst en parsen elk naar int.
    #
    # EDGE CASE: er is altijd minstens één INTEGER (de grammar dwingt + af),
    # maar we behandelen de lijst generiek zodat we altijd correct werken.
    def visitArrayDec(self, ctx):
        # stap 1: het type van de elementen
        var_type = self.visit(ctx.type_())

        # stap 2: de naam van de array variabele
        name = ctx.ID().getText()

        # stap 3: de dimensies — ctx.INTEGER() geeft een lijst van tokens
        # Voorbeeld: int arr[2][4] → ctx.INTEGER() = [Token('2'), Token('4')]
        dimensions = [int(tok.getText()) for tok in ctx.INTEGER()]

        # stap 4: de optionele initialisator
        # ctx.arrayInit() geeft None terug als er geen '= {...}' is
        if ctx.arrayInit():
            initializer = self.visit(ctx.arrayInit())
        else:
            initializer = None

        return ArrayDeclNode(var_type, name, dimensions, initializer)

    # --------------------------------------------------------
    # visitArrayInit: array initialisator { ... }
    # --------------------------------------------------------
    # Grammar: arrayInit : LBRACE (arrayElement (COMMA arrayElement)*)? RBRACE
    #
    # EDGE CASE: lege initialisator {} → ArrayInitNode([])
    # De grammar maakt de inhoud optioneel via de ? → we checken ctx.arrayElement()
    # die een lege lijst teruggeeft als er geen elementen zijn.
    def visitArrayInit(self, ctx):
        elements = []
        for elem_ctx in ctx.arrayElement():
            elements.append(self.visit(elem_ctx))
        return ArrayInitNode(elements)

    # --------------------------------------------------------
    # visitArrayElement: één element in een initialisator
    # --------------------------------------------------------
    # Grammar: arrayElement : expression | arrayInit
    #
    # EDGE CASE: we moeten onderscheid maken tussen een expressie en
    # een geneste initialisator. We checken ctx.arrayInit() eerst.
    def visitArrayElement(self, ctx):
        if ctx.arrayInit():
            return self.visit(ctx.arrayInit())
        return self.visit(ctx.expression())

    # --------------------------------------------------------
    # visitFunctionCall: printf(...) of scanf(...)
    # --------------------------------------------------------
    # Grammar: functionCall : ID LPAREN (expression (COMMA expression)*)? RPAREN
    #
    # EDGE CASE: geen argumenten → ctx.expression() geeft lege lijst terug.
    # De ? in de grammar maakt de hele argumentenlijst optioneel.
    #
    # EDGE CASE: ctx.expression() geeft hier een LIJST terug omdat expression
    # meerdere keren voorkomt in de regel. Dat is anders dan in varDec waar
    # expression maar één keer voorkomt!
    def visitFunctionCall(self, ctx):
        name = ctx.ID().getText()

        # ctx.expression() geeft een lijst van alle argumenten (kan leeg zijn)
        args = []
        for expr_ctx in ctx.expression():
            args.append(self.visit(expr_ctx))

        return FunctionCallNode(name, args)

    # --------------------------------------------------------
    # visitComment: // of /* */
    # --------------------------------------------------------
    # Grammar: comment : LINE_COMMENT_TOKEN | BLOCK_COMMENT_TOKEN
    #
    # We slaan de volledige token tekst op, inclusief de // of /* */ delimiters.
    #
    # EDGE CASE: ctx.LINE_COMMENT_TOKEN() of ctx.BLOCK_COMMENT_TOKEN() kan
    # None zijn als het het andere type is. We checken welke aanwezig is.
    def visitComment(self, ctx):
        if ctx.LINE_COMMENT_TOKEN():
            text = ctx.LINE_COMMENT_TOKEN().getText()
        else:
            text = ctx.BLOCK_COMMENT_TOKEN().getText()
        return CommentNode(text)

    # --------------------------------------------------------
    # visitExpression: het hart van de visitor (uitgebreid)
    # --------------------------------------------------------
    # Nieuw in assignment 3:
    #   ① STRING literal        → StringLiteralNode
    #   ② functionCall als expr → FunctionCallNode (via visitFunctionCall)
    #   ③ array toegang         → ArrayAccessNode
    #      expr[expr] heeft 4 kinderen: expr, '[', expr, ']'
    #      LET OP: cast LPAREN type RPAREN expr heeft ook 4 kinderen!
    #      We onderscheiden ze door kind 1 te inspecteren:
    #        kind 1 == '[' → array toegang
    #        kind 0 == '(' → cast
    def visitExpression(self, ctx):
        child_count = ctx.getChildCount()

        # ── GEVAL 1: INTEGER literal ────────────────────────────────────────
        if ctx.INTEGER():
            return LiteralNode(int(ctx.INTEGER().getText()), 'int')

        # ── GEVAL 2: FLOAT literal ──────────────────────────────────────────
        if ctx.FLOAT():
            return LiteralNode(float(ctx.FLOAT().getText()), 'float')

        # ── GEVAL 3: CHAR literal ───────────────────────────────────────────
        if ctx.CHAR():
            tekst = ctx.CHAR().getText()   # bv. "'a'" of "'\\n'"
            inner = tekst[1:-1]            # verwijder de omringende quotes

            if inner.startswith('\\'):
                escape_map = {
                    'n': '\n', 't': '\t', 'r': '\r',
                    'b': '\b', 'f': '\f', '\\': '\\', "'": "'"
                }
                waarde = escape_map.get(inner[1], inner[1])
            else:
                waarde = inner

            return LiteralNode(waarde, 'char')

        # ── GEVAL 4: STRING literal (NIEUW) ─────────────────────────────────
        # Voorbeeld: "hello\n" → StringLiteralNode("hello\n")
        #
        # EDGE CASE: ctx.STRING().getText() geeft de tekst MET aanhalingstekens
        # terug, bv. '"hello\\n"'. We slaan de tekst ZONDER aanhalingstekens op.
        # We doen GEEN escape processing hier — dat is de taak van de LLVM visitor.
        #
        # EDGE CASE: lege string "" → getText() = '""' → value = ''
        if ctx.STRING():
            raw = ctx.STRING().getText()    # '"hello\\n"'
            value = raw[1:-1]               # 'hello\\n' (zonder quotes)
            return StringLiteralNode(value)

        # ── GEVAL 5: variabele (identifier) ────────────────────────────────
        if ctx.ID():
            return VariableNode(ctx.ID().getText())

        # ── GEVAL 6: functionCall als expressie (NIEUW) ─────────────────────
        # Voorbeeld: int n = printf("hello");
        # ANTLR plaatst een functionCall sub-context als kind.
        # We delegeren naar visitFunctionCall.
        #
        # BELANGRIJK: dit moet VOOR de child_count logica komen, want
        # een functionCall heeft variabel aantal kinderen en wordt anders
        # verward met een binaire operatie.
        if ctx.functionCall():
            return self.visit(ctx.functionCall())

        # ── GEVAL 7: cast → (type) expression ──────────────────────────────
        # Structuur: LPAREN type RPAREN expression → 4 kinderen
        # We herkennen dit doordat er een type()-kind is.
        # MOET voor de child_count == 4 check komen!
        if ctx.type_():
            target_type = self.visit(ctx.type_())
            operand     = self.visit(ctx.expression(0))
            return CastNode(target_type, operand)

        # ── GEVAL 8: haakjes → ( expression ) ──────────────────────────────
        # 3 kinderen: '(', expression, ')'
        if child_count == 3 and ctx.getChild(0).getText() == '(':
            return self.visit(ctx.expression(0))

        # ── GEVAL 9: array toegang → expression[expression] (NIEUW) ────────
        # Structuur: expression LBRACKET expression RBRACKET → 4 kinderen
        # We herkennen dit doordat kind[1].getText() == '['.
        #
        # EDGE CASE: arr[i][j] wordt door ANTLR als links-associatief geparseerd:
        #   ((arr[i])[j])
        # De recursieve expressie aan de linkerkant is al een ArrayAccessNode,
        # en dit wordt gewoon de array_expr van de buitenste ArrayAccessNode.
        # We hoeven hier niets speciaals te doen — het werkt automatisch!
        if child_count == 4 and ctx.getChild(1).getText() == '[':
            array_expr = self.visit(ctx.expression(0))  # de array
            index      = self.visit(ctx.expression(1))  # de index
            return ArrayAccessNode(array_expr, index)

        # ── GEVAL 10: unaire operatoren (2 kinderen) ────────────────────────
        # Suffix: expression OP  (kind 0 is expr, kind 1 is operator)
        # Prefix: OP expression  (kind 0 is operator, kind 1 is expr)
        if child_count == 2:
            first = ctx.getChild(0).getText()
            last  = ctx.getChild(1).getText()

            if last == '++':
                return UnaryOpNode('suffix++', self.visit(ctx.expression(0)))
            if last == '--':
                return UnaryOpNode('suffix--', self.visit(ctx.expression(0)))
            if first == '++':
                return UnaryOpNode('prefix++', self.visit(ctx.expression(0)))
            if first == '--':
                return UnaryOpNode('prefix--', self.visit(ctx.expression(0)))

            # alle andere unaire prefix operatoren: -, +, !, ~, &, *
            return UnaryOpNode(first, self.visit(ctx.expression(0)))

        # ── GEVAL 11: binaire operatie (3 kinderen) ─────────────────────────
        # Structuur: expression OPERATOR expression
        if child_count == 3:
            left     = self.visit(ctx.expression(0))
            operator = ctx.getChild(1).getText()
            right    = self.visit(ctx.expression(1))
            return BinaryOpNode(operator, left, right)

        # ── GEVAL 12: onverwacht ─────────────────────────────────────────────
        raise ValueError(
            f"Onverwacht patroon in expression: {ctx.getText()!r} "
            f"(aantal kinderen: {child_count})"
        )