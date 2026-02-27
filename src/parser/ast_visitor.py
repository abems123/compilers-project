# src/parser/ast_visitor.py

from antlr4 import ParseTreeVisitor
from .ast_nodes import LiteralNode, BinaryOpNode, UnaryOpNode


#CSTtoASTVisitor: dit klasse zal CST omzetten in AST
class CSTtoASTVisitor(ParseTreeVisitor):


    #dit mehtode loopt door alle expression kinderen en bezoekt elk van hen
    #het resultaat is een lijst van ASTnodes, 1 per expressie.
    # ctx is de context-knoop van ANTLR voor de 'file' regel.
    def visitProgram(self, ctx):

        #een lijst waar we de resultaten in stoppen.
        ast_nodes = []

        """
        Ik heb in dit stuk effe AI gebruikt om te snappen hoe ik met cst boom nodes moest werken
        """

        # Loop door elke expressie in de file
        # ctx.expression() geeft bv. [expr1, expr2, expr3]
        for expression_ctx in ctx.expression():

            # Bezoek de expressie → dit geeft een ASTNode terug
            # (een LiteralNode, BinaryOpNode, of UnaryOpNode)
            ast_node = self.visit(expression_ctx)

            # Voeg het toe aan onze lijst
            ast_nodes.append(ast_node)

        return ast_nodes

    #dit methode beslist welk ASTNode het zal terug geven. beslissing gebeurt op basis van het aantal kinderen
    def visitExpression(self, ctx):

        #ctx.getChildCount() geeft het aantal kinderen
        child_count = ctx.getChildCount()


        #geval 1: alleen een integer
        if child_count == 1:

            #ctx.INTEGER() geeft het INTEGER token terug
            #.getText() geeft de tekst ervan: "42"
            #int(...) zet de tekst om naar een Python int
            waarde = int(ctx.INTEGER().getText())

            # type_name='int' want we werken nu alleen met integers
            return LiteralNode(waarde, 'int')

        #geval 2: 3 knderen waarvan 2 zijn haken en 1 is expression. we gooien de haken weg en kijken naar de expression)
        elif child_count == 3 and ctx.getChild(0).getText() == '(':

            #self.visit() roept automatisch de juiste methode op
            return self.visit(ctx.getChild(1))

        # ── GEVAL 3: binaire operatie → expr op expr ─────────
        # De expressie is een operatie met twee operanden
        # Er zijn 3 kinderen: expression, operator, expression
        # Voorbeeld boom voor "3 + 4":
        #   expression
        #     ├── expression (3)   ← linkerkind
        #     ├── +                ← operator
        #     └── expression (4)   ← rechterkind

        #geval 3: 3 kinderen waarvan 2 operanden zijn en 1 een operatie (binariy operation gewoon)
        elif child_count == 3:

            #bezoek het linker kind eerst. dit geeft een ASTNode terug
            left = self.visit(ctx.getChild(0))

            #haal de operator als tekst
            operator = ctx.getChild(1).getText()

            #bezoek het rechter kind. dit geeft een ASTNode terug
            right = self.visit(ctx.getChild(2))

            #maak een BinaryOpNode met links, operator, rechts
            return BinaryOpNode(operator, left, right)

        #geval 4: 2 kinderen -> unaire operatie: 1 operator en 1 operand
        elif child_count == 2:
            #haal de operator op. geeft een ASTNode terug
            operator = ctx.getChild(0).getText()

            #bezoek het kind. geeft een ASTNode terug
            operand = self.visit(ctx.getChild(1))

            return UnaryOpNode(operator, operand)

        # ── GEVAL 5: iets onverwachts ─────────────────────────
        # Dit zou normaal nooit mogen gebeuren.
        # Als het toch gebeurt, gooien we een fout
        # zodat je meteen weet dat er iets mis is.

        #voor nu: als er meer of minder kinderen zijn dan ik verwacht heb dan krijgen we gwn error en we kunnen hierna debuggen
        #dit heb ik gemaakt just in case dat mijn logica ergens niet klopte of als we ooit iets gaan updaten.
        else:
            raise ValueError(
                f"Onverwacht aantal kinderen in expression: {child_count}"
                f"\nTekst: {ctx.getText()}"
            )