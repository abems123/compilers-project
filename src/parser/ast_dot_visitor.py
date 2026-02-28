# src/parser/ast_dot_visitor.py
from __future__ import annotations

class ASTDotVisitor:
    """
    Visits your AST nodes and emits Graphviz DOT.
    Returns the graphviz node-id (string) for each visited AST node.
    With Nodes written like this: n(id) [label="(Node name)];)
    WIth Edges written like this: n(id) -- n(id) [label="(Edge name)];
    """

    def __init__(self):
        self._next_id = 0
        self.lines = []
        self.lines.append("graph \"\"")
        self.lines.append("{")
        self.lines.append("node [shape=box];")



    def new_id(self):
        self._next_id += 1
        return f"n{self._next_id}"

    def create_node(self, node_id, label):
        self.lines.append(f'  {node_id} [label=\"{label}\"];')

    def create_edge(self, src, dst, edge_label = None):
        if edge_label is None:
            self.lines.append(f"  {src} -- {dst};")
        else:
            self.lines.append(f'  {src} -- {dst} [label=\"{edge_label}\"];')

    # ---- The 3 methods your AST nodes will call via accept() ----
    def visitLiteral(self, node):
        my_id = self.new_id()
        self.create_node(my_id, f"Literal({node.value})")
        return my_id

    def visitUnaryOp(self, node):
        my_id = self.new_id()
        self.create_node(my_id, f"UnaryOp({node.op})")

        child_id = node.operand.accept(self)
        self.create_edge(my_id, child_id, "operand")
        return my_id

    def visitBinaryOp(self, node):
        my_id = self.new_id()
        self.create_node(my_id, f"BinaryOp({node.op})")

        left_id = node.left.accept(self)
        right_id = node.right.accept(self)

        self.create_edge(my_id, left_id, "left")
        self.create_edge(my_id, right_id, "right")
        return my_id

    def finalize(self):
        self.lines.append("}")
        return "\n".join(self.lines)