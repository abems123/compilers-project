# src/parser/constant_folding_visitor.py

from .ast_nodes import LiteralNode, BinaryOpNode, UnaryOpNode


class ConstantFoldingVisitor:

    #geeft de LiteralNode terug. dit is het simpelste node waar momenteel niks ermee moet gebeuren
    def visitLiteral(self, node):
        return node


    #dit functie wordt in 2 stappen uitgevoerd: stap 1: bezoek de kinderen eerst. stap2: check of beide kinderen nu LiteralNodes zijn
    def visitBinaryOp(self, node):

        #stap 1: bezoek de kinderen eerst (recursief)
        left  = node.left.accept(self)
        right = node.right.accept(self)

        #stap 2: we kijken of beide kinderen nu literals zijn

        #als wel:
        if isinstance(left, LiteralNode) and isinstance(right, LiteralNode):

            #als wel dan halen we de waardes uit
            l = left.value
            r = right.value

            #bereken het resultaat op basis van de operator
            if node.op == '+':
                resultaat = l + r

            elif node.op == '-':
                resultaat = l - r

            elif node.op == '*':
                resultaat = l * r

            #NOTE: ik heb devision elif statement adhv AI gedaan want ik wist nie zeker welk edge cases er waren of hoe de ding moet gedragen op basis van de type
            #want integer devision is anders dan float devision
            elif node.op == '/':
                # Let op: integer deling!
                # In C is 5 / 2 = 2, niet 2.5
                if r == 0:
                    raise ZeroDivisionError(
                        f"Deling door nul gevonden: {l} / {r}"
                    )
                resultaat = l // r

            elif node.op == '%':
                if r == 0:
                    raise ZeroDivisionError(
                        f"Modulo door nul gevonden: {l} % {r}"
                    )
                resultaat = l % r

            elif node.op == '==':
                #ture en false moet naar 1 of 0 omgezet worden, daarop die "int"
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
                raise ValueError(f"Onbekende operator: {node.op}")

            #return een nieuwe LiteralNode terug met het resultaat (de hele BinaryOpNode is nu vervangen door 1 getal)
            return LiteralNode(resultaat, 'int')

        # Stap 2b: niet beide literals
        # We kunnen niet berekenen, maar we geven wel de
        # gevouwen kinderen mee (left en right zijn al bezocht)

        #als niet: kan niet berekend worden. (misschien de kinderen konden wel berekend worden maar die node zelf niet. we geven de "nieuwe" kinderen mee (nieuw in de zin van als ze verwerkt werden))
        return BinaryOpNode(node.op, left, right)


    #zelfde logica als bij visitBinaryOp maar met 1 kind. het gebeurt dus in 2 stappen:
    def visitUnaryOp(self, node):

        #stap 1: bezoek het kind eerst
        operand = node.operand.accept(self)

        #stap 2: is het kind een literal

        #als wel
        if isinstance(operand, LiteralNode):

            v = operand.value

            if node.op == '-':
                resultaat = -v

            elif node.op == '+':
                resultaat = +v

            elif node.op == '!':
                resultaat = int(not bool(v))

            elif node.op == '~':
                resultaat = ~v

            else:
                raise ValueError(f"Onbekende unaire operator: {node.op}")

            return LiteralNode(resultaat, 'int')

        #als niet
        return UnaryOpNode(node.op, operand)