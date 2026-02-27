#ASTNode: basisklasse voor de verschillende soorten Nodes om hiervan te inheriten.
class ASTNode:

    #accept methode kunnen we zien als een visitor van nodes. die zal bij een node van CST komen en dan beslissen wat die hiermaa gaat doen
    #deze methode moet gedefinieerd worden door al de klasses die van ASTNode inheriten.
    def accept(self, visitor):
        raise NotImplementedError("Elke subklasse moet accept() implementeren")


#LiteralNode: dit is een blad node (heeft geen kinderen) voor getallen zoals 1, 3, 20 enzo.
#deze inherit van ASTNode basisklasse
class LiteralNode(ASTNode):

    def __init__(self, value, type_name: str):

        self.value = value

        #type van de literal (we werken nu met integers maar later gaan we ook met floats, doubles enzo moeten werken).
        self.type_name = type_name

    def accept(self, visitor):
        #Roept visitLiteral() op van de visitor. Elke visitor die met LiteralNodes werkt moet een methode visitLiteral(node) hebben.
        return visitor.visitLiteral(self)

    def __repr__(self):
        #print(node) geeft leesbare output. dit is puur voor debuggen.
        return f"LiteralNode({self.value})"

#BinaryOpNode: een operatie met 2 operanden. dit node type heeft 2 kinderen nodes
class BinaryOpNode(ASTNode):

    def __init__(self, op: str, left: ASTNode, right: ASTNode):

        self.op = op
        self.left = left
        self.right = right

    def accept(self, visitor):
        return visitor.visitBinaryOp(self)


    def __repr__(self):
        #print(node) geeft leesbare output. dit is puur voor debuggen.
        return f"BinaryOpNode('{self.op}', {self.left}, {self.right})"

#UnaryOpNode: operatie met 1 operand. bv -3 of !true enzo. dit node type heeft 1 kind node.
#bv: -3 = UnaryOpNode(-)->ASTNode()
class UnaryOpNode(ASTNode):

    def __init__(self, op: str, operand: ASTNode):

        self.op = op
        self.operand = operand

    def accept(self, visitor):
        return visitor.visitUnaryOp(self)

    def __repr__(self):
        # print(node) geeft leesbare output. dit is puur voor debuggen.
        return f"UnaryOpNode('{self.op}', {self.operand})"