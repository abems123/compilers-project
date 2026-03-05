# src/parser/constant_folding_visitor.py

from .ast_nodes import (
    LiteralNode, BinaryOpNode, UnaryOpNode,
    VariableNode, VarDeclNode, AssignNode,
    CastNode, TypeNode, BlockNode, ProgramNode,
    # Nieuw in assignment 3:
    CommentNode, ArrayDeclNode, ArrayInitNode,
    ArrayAccessNode, StringLiteralNode,
    FunctionCallNode, IncludeNode
)


class ConstantFoldingVisitor:
    """
    Doet twee dingen in één pass over de AST:

    1. Constant Folding: berekent expressies met alleen literals op compile-time.
       Voorbeeld: 3 + 4  →  LiteralNode(7)

    2. Constant Propagation: vervangt variabelen met bekende waarden door hun literal.
       Voorbeeld: const int x = 5; int y = x + 3;  →  int y = 8;

    Assignment 3 uitbreiding:
      De nieuwe node types (Comment, ArrayDecl, ArrayInit, ArrayAccess,
      StringLiteral, FunctionCall, Include) worden grotendeels ongewijzigd
      doorgegeven — we vouwen geen arrays of functie-aanroepen.

      Uitzondering: de expressies BINNEN array initialisatoren en functie-
      argumenten worden WEL gevouwen als ze constant zijn.
      Voorbeeld: int arr[3] = {1+2, 4, 5*1};  →  {3, 4, 5}
    """

    def __init__(self):
        # dict van variabelenaam → LiteralNode met de bekende waarde
        self.known_values = {}

        # dict van variabelenaam → bool (is het een const variabele?)
        self.is_const = {}

    # ============================================================
    # STRUCTUUR: program, block, statements
    # ============================================================

    def visitProgram(self, node):
        # NIEUW: geef includes door aan de nieuwe ProgramNode
        new_body = node.body.accept(self)
        return ProgramNode(new_body, node.includes)

    def visitBlock(self, node):
        new_statements = []
        for stmt in node.statements:
            new_stmt = stmt.accept(self)
            new_statements.append(new_stmt)
        return BlockNode(new_statements)

    def visitVarDecl(self, node):
        if node.value is not None:
            new_value = node.value.accept(self)
        else:
            new_value = None

        if (isinstance(new_value, LiteralNode)
                and node.var_type.base_type == 'float'
                and new_value.type_name == 'int'):
            new_value = LiteralNode(float(new_value.value), 'float')

        if isinstance(new_value, LiteralNode):
            self.known_values[node.name] = new_value
            self.is_const[node.name] = node.var_type.is_const

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
    # NIEUW: ARRAY NODES
    # ============================================================

    def visitArrayDecl(self, node):
        """
        Array declaraties kunnen we niet als geheel vouwen, maar de
        expressies IN de initialisator wel.

        Voorbeeld:
          int arr[3] = {1+2, x, 5*1};
          → als x bekend is: {3, x_waarde, 5}
          → als x onbekend is: {3, x, 5}

        BELANGRIJK: arrays komen NIET in known_values terecht.
        Constant propagation voor array elementen is te complex
        (we weten niet welk element op runtime gebruikt wordt).
        """
        if node.initializer is not None:
            new_init = node.initializer.accept(self)
        else:
            new_init = None

        return ArrayDeclNode(node.var_type, node.name, node.dimensions, new_init)

    def visitArrayInit(self, node):
        """
        Vouw de expressies in een array initialisator.
        Geneste ArrayInitNodes worden ook recursief gevouwen.
        """
        new_elements = []
        for elem in node.elements:
            new_elements.append(elem.accept(self))
        return ArrayInitNode(new_elements)

    def visitArrayAccess(self, node):
        """
        Array toegang: vouw de index expressie als mogelijk.
        Voorbeeld: arr[2+1]  →  arr[3]

        We vouwen de array_expr en index beide, maar het resultaat
        is altijd een ArrayAccessNode — we kunnen niet op compile-time
        bepalen wat de waarde van arr[i] is.
        """
        new_array_expr = node.array_expr.accept(self)
        new_index      = node.index.accept(self)
        return ArrayAccessNode(new_array_expr, new_index)

    # ============================================================
    # NIEUW: COMMENT, INCLUDE, STRING, FUNCTIONCALL
    # ============================================================

    def visitComment(self, node):
        """
        Comments worden ongewijzigd doorgegeven.
        Er valt niets te vouwen in een comment.
        """
        return node

    def visitInclude(self, node):
        """
        Include nodes worden ongewijzigd doorgegeven.
        """
        return node

    def visitStringLiteral(self, node):
        """
        String literals worden ongewijzigd doorgegeven.
        Een string is al zo simpel als het kan.
        """
        return node

    def visitFunctionCall(self, node):
        """
        Functie-aanroepen kunnen we niet vouwen (we kennen de return waarde
        niet op compile-time), maar de argumenten WEL.

        Voorbeeld:
          printf("%d\n", 3 + 4)  →  printf("%d\n", 7)
        """
        new_args = []
        for arg in node.args:
            new_args.append(arg.accept(self))
        return FunctionCallNode(node.name, new_args)

    # ============================================================
    # CONSTANT PROPAGATION: variabelen vervangen door hun waarde
    # ============================================================

    def visitVariable(self, node):
        if node.name in self.known_values:
            return self.known_values[node.name]
        return node

    # ============================================================
    # EXPRESSIES: folding (ongewijzigd van assignment 2)
    # ============================================================

    def visitLiteral(self, node):
        return node

    def visitBinaryOp(self, node):
        left  = node.left.accept(self)
        right = node.right.accept(self)

        if isinstance(left, LiteralNode) and isinstance(right, LiteralNode):
            l = left.value
            r = right.value

            if node.op == '+':
                resultaat = l + r
            elif node.op == '-':
                resultaat = l - r
            elif node.op == '*':
                resultaat = l * r
            elif node.op == '/':
                if r == 0:
                    raise ZeroDivisionError(f"Deling door nul: {l} / {r}")
                if left.type_name == 'int' and right.type_name == 'int':
                    resultaat = l // r
                else:
                    resultaat = l / r
            elif node.op == '%':
                if r == 0:
                    raise ZeroDivisionError(f"Modulo door nul: {l} % {r}")
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
                raise ValueError(f"Onbekende operator: {node.op}")

            result_type = 'float' if (left.type_name == 'float' or right.type_name == 'float') else 'int'
            return LiteralNode(resultaat, result_type)

        return BinaryOpNode(node.op, left, right)

    def visitUnaryOp(self, node):
        operand = node.operand.accept(self)

        # ++ en -- hebben side effects → niet folden
        if node.op in ('prefix++', 'prefix--', 'suffix++', 'suffix--'):
            if isinstance(node.operand, VariableNode):
                self.known_values.pop(node.operand.name, None)
            return UnaryOpNode(node.op, node.operand)

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
            elif node.op == '&':
                # address-of: gebruik de ORIGINELE operand, niet de gepropageerde waarde.
                # &x moet het adres van x zelf teruggeven, niet &5 als x=5 bekend is.
                return UnaryOpNode('&', node.operand)
            elif node.op == '*':
                return UnaryOpNode('*', operand)
            else:
                raise ValueError(f"Onbekende unaire operator: {node.op}")

            return LiteralNode(resultaat, operand.type_name)

        return UnaryOpNode(node.op, operand)

    def visitCast(self, node):
        operand = node.operand.accept(self)

        if isinstance(operand, LiteralNode):
            target = node.target_type.base_type

            if target == 'int':
                return LiteralNode(int(operand.value), 'int')
            elif target == 'float':
                return LiteralNode(float(operand.value), 'float')
            elif target == 'char':
                return LiteralNode(chr(int(operand.value)), 'char')

        return CastNode(node.target_type, operand)

    def visitType(self, node):
        return node