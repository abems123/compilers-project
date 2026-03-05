#ASTNode: basisklasse voor de verschillende soorten Nodes om hiervan te inheriten.
class ASTNode:

    #accept methode kunnen we zien als een visitor van nodes. die zal bij een node van CST komen en dan beslissen wat die hiermaa gaat doen
    #deze methode moet gedefinieerd worden door al de klasses die van ASTNode inheriten.
    def accept(self, visitor):
        raise NotImplementedError("Elke subklasse moet accept() implementeren")


#TypeNode beschrijft een type zoals: int, const float*, char**
class TypeNode(ASTNode):

    def __init__(self, base_type: str, pointer_depth: int = 0, is_const: bool = False):
        # basistype: 'int', 'float', of 'char'
        self.base_type = base_type

        # hoe diep zit de pointer? 0 = geen pointer, 1 = *, 2 = **, enz.
        self.pointer_depth = pointer_depth

        # is de waarde waarnaar gewezen wordt constant?
        # const int* heeft is_const=True
        self.is_const = is_const

    def accept(self, visitor):
        return visitor.visitType(self)

    def __repr__(self):
        const_str = "const " if self.is_const else ""
        stars = "*" * self.pointer_depth
        return f"TypeNode({const_str}{self.base_type}{stars})"


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


#VariableNode: een identifier die in een expressie voorkomt.
#Later zal de semantic analysis visitor dit node opzoeken in de symbol table om het type te bepalen.

#NOTE: Dit is geen declaratie. dat is VarDeclNode hieronder. met andere woorden dit is gewoon het gebruik van een variabele in een expressie.
class VariableNode(ASTNode):

    def __init__(self, name: str):
        #de naam van de variabele zoals die in de broncode staat
        self.name = name

    def accept(self, visitor):
        return visitor.visitVariable(self)

    def __repr__(self):
        return f"VariableNode({self.name!r})"



# Merk op: de initialisatiewaarde is een gewone ASTNode (expressie).
# Als er geen initialisatie is, is value=None.

#VarDeclNode: een variabele declaratie, met of zonder initialisatie.
#de initialisatiewaarde is een gewone ASTNode (expressie). Als er geen initialisatie is, is value=None.
class VarDeclNode(ASTNode):

    def __init__(self, var_type: TypeNode, name: str, value: ASTNode = None):
        #het type van de variabele (inclusief const en pointer-diepte)
        self.var_type = var_type

        #de naam van de variabele
        self.name = name

        #de initialisatiewaarde (expressie), of None als er geen is
        self.value = value

    def accept(self, visitor):
        return visitor.visitVarDecl(self)

    def __repr__(self):
        return f"VarDeclNode({self.var_type}, {self.name!r}, value={self.value})"





#AssignNode: een assignment statement.
#De linkerkant is een expressie (lvalue) en de rechterkant ook.
#NOTE: dit was een beetje confusing en ik moest AI voor hulp vragen. mijn code was een beetje fout dus de AI heeft het code geupdate naar iets accurater

#wat AI zei:
# Waarom is de linkerkant een expressie en geen gewone naam?
# Omdat je in C ook pointer dereferences kan assignen:
#   *ptr = 5;    → linkerkant is UnaryOpNode('*', VariableNode('ptr'))
#   x = 5;       → linkerkant is VariableNode('x')
#
# De semantic analysis visitor zal later controleren of de
# linkerkant een geldige lvalue is (geen const, geen rvalue).

class AssignNode(ASTNode):

    def __init__(self, target: ASTNode, value: ASTNode):
        # de linkerkant: VariableNode of UnaryOpNode('*', ...)
        self.target = target

        # de rechterkant: een willekeurige expressie
        self.value = value

    def accept(self, visitor):
        return visitor.visitAssign(self)

    def __repr__(self):
        return f"AssignNode({self.target}, {self.value})"


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


# CastNode: een expliciete type cast.
#
# Voorbeeld:
#   (int) x       → CastNode(TypeNode('int'), VariableNode('x'))
#   (float) 3     → CastNode(TypeNode('float'), LiteralNode(3, 'int'))
#   (int*) ptr    → CastNode(TypeNode('int', pointer_depth=1), VariableNode('ptr'))
#
# Waarom een aparte node en geen UnaryOpNode?
# Omdat de operator hier een TYPE is, geen symbool.
# De semantic analysis moet het doeltype kennen voor type checking.
class CastNode(ASTNode):

    def __init__(self, target_type: TypeNode, operand: ASTNode):
        # het type waar naartoe gecast wordt
        self.target_type = target_type

        # de expressie die gecast wordt
        self.operand = operand

    def accept(self, visitor):
        return visitor.visitCast(self)

    def __repr__(self):
        return f"CastNode({self.target_type}, {self.operand})"


#BlockNode: een blok van statements tussen accolades { ... }. Bevat een lijst van ASTNodes (de statements).
class BlockNode(ASTNode):

    def __init__(self, statements: list):
        #een lijst van ASTNodes, elk een statement
        self.statements = statements

    def accept(self, visitor):
        return visitor.visitBlock(self)

    def __repr__(self):
        return f"BlockNode({self.statements})"


#ProgramNode: de root van de hele AST. Stelt de int main() { ... } functie voor.
class ProgramNode(ASTNode):

    def __init__(self, body: BlockNode):
        #de body is de BlockNode van de main functie
        self.body = body

    def accept(self, visitor):
        return visitor.visitProgram(self)

    def __repr__(self):
        return f"ProgramNode({self.body})"