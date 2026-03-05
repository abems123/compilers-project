# src/parser/ast_dot_visitor.py

class ASTDotVisitor:
    """
    Bezoekt alle AST nodes en genereert Graphviz DOT formaat.

    Elke visit methode:
      1. Maakt een nieuw node-id aan
      2. Maakt een DOT node met een label
      3. Bezoekt de kinderen (recursief via node.accept(self))
      4. Maakt een edge van zichzelf naar elk kind
      5. Geeft het eigen node-id terug aan de parent

    De parent gebruikt dat id om een edge naar dit node te tekenen.
    Zo bouwt de DOT graph zich recursief op van boven naar beneden.
    """

    def __init__(self):
        self._next_id = 0
        self.lines = []
        self.lines.append('graph ""')
        self.lines.append("{")
        self.lines.append("  node [shape=box];")

    def new_id(self):
        """Geeft een uniek node-id terug: n1, n2, n3, ..."""
        self._next_id += 1
        return f"n{self._next_id}"

    def create_node(self, node_id, label):
        """Schrijft een DOT node definitie: n1 [label="..."];"""
        # We escapen de aanhalingstekens in het label zodat DOT niet crasht
        safe_label = label.replace('"', '\\"')
        self.lines.append(f'  {node_id} [label="{safe_label}"];')

    def create_edge(self, src, dst, edge_label=None):
        """Schrijft een DOT edge: n1 -- n2;  of  n1 -- n2 [label="..."];"""
        if edge_label is None:
            self.lines.append(f"  {src} -- {dst};")
        else:
            self.lines.append(f'  {src} -- {dst} [label="{edge_label}"];')

    def finalize(self):
        """Sluit de DOT graph af en geeft de volledige string terug."""
        self.lines.append("}")
        return "\n".join(self.lines)

    # ============================================================
    # STRUCTUUR NODES
    # ============================================================

    def visitProgram(self, node):
        """
        ProgramNode: de root van de AST.
        Heeft één kind: de body (BlockNode van main).

        DOT voorbeeld:
          n1 [label="Program (main)"];
          n1 -- n2 [label="body"];
        """
        my_id = self.new_id()
        self.create_node(my_id, "Program (main)")

        body_id = node.body.accept(self)
        self.create_edge(my_id, body_id, "body")

        return my_id

    def visitBlock(self, node):
        """
        BlockNode: een blok van statements { ... }.
        Heeft nul of meer kinderen: de statements.

        DOT voorbeeld voor { int x = 5; x = x + 1; }:
          n2 [label="Block"];
          n2 -- n3 [label="stmt[0]"];
          n2 -- n7 [label="stmt[1]"];
        """
        my_id = self.new_id()
        self.create_node(my_id, "Block")

        for i, stmt in enumerate(node.statements):
            stmt_id = stmt.accept(self)
            self.create_edge(my_id, stmt_id, f"stmt[{i}]")

        return my_id

    # ============================================================
    # DECLARATIE EN ASSIGNMENT NODES
    # ============================================================

    def visitVarDecl(self, node):
        """
        VarDeclNode: variabele declaratie, met of zonder initialisatie.

        DOT voorbeeld voor  const int* p = &x :
          n3 [label="VarDecl: p\\nconst int*"];
          n3 -- n4 [label="type"];
          n3 -- n5 [label="init"];

        We tonen het type direct in het label voor leesbaarheid,
        maar tekenen ook een aparte type-edge zodat je de TypeNode ziet.
        """
        my_id = self.new_id()

        # bouw een leesbaar label: naam + type info
        type_str = repr(node.var_type).replace("TypeNode(", "").rstrip(")")
        self.create_node(my_id, f"VarDecl: {node.name}\\n{type_str}")

        # teken de TypeNode als kind
        type_id = node.var_type.accept(self)
        self.create_edge(my_id, type_id, "type")

        # als er een initialisatiewaarde is, teken die ook
        if node.value is not None:
            value_id = node.value.accept(self)
            self.create_edge(my_id, value_id, "init")

        return my_id

    def visitAssign(self, node):
        """
        AssignNode: assignment statement (target = value).

        DOT voorbeeld voor  *ptr = 5 :
          n4 [label="Assign"];
          n4 -- n5 [label="target"];
          n4 -- n6 [label="value"];
        """
        my_id = self.new_id()
        self.create_node(my_id, "Assign")

        target_id = node.target.accept(self)
        self.create_edge(my_id, target_id, "target")

        value_id = node.value.accept(self)
        self.create_edge(my_id, value_id, "value")

        return my_id

    # ============================================================
    # TYPE NODE
    # ============================================================

    def visitType(self, node):
        """
        TypeNode: een type zoals int, const float*, int**.

        We bouwen het label zo:
          const int**  →  "Type: const int**"
          float        →  "Type: float"
        """
        my_id = self.new_id()

        const_str = "const " if node.is_const else ""
        stars     = "*" * node.pointer_depth
        self.create_node(my_id, f"Type: {const_str}{node.base_type}{stars}")

        return my_id

    # ============================================================
    # EXPRESSIE NODES
    # ============================================================

    def visitLiteral(self, node):
        """
        LiteralNode: een concrete waarde (int, float of char).

        DOT voorbeeld:
          n5 [label="Literal: 42 (int)"];
        """
        my_id = self.new_id()
        self.create_node(my_id, f"Literal: {node.value!r} ({node.type_name})")
        return my_id

    def visitVariable(self, node):
        """
        VariableNode: een identifier in een expressie.

        DOT voorbeeld voor  x :
          n6 [label="Var: x"];
        """
        my_id = self.new_id()
        self.create_node(my_id, f"Var: {node.name}")
        return my_id

    def visitBinaryOp(self, node):
        """
        BinaryOpNode: een binaire operatie met links en rechts.

        DOT voorbeeld voor  3 + 4 :
          n7 [label="BinaryOp: +"];
          n7 -- n8 [label="left"];
          n7 -- n9 [label="right"];
        """
        my_id = self.new_id()
        self.create_node(my_id, f"BinaryOp: {node.op}")

        left_id  = node.left.accept(self)
        right_id = node.right.accept(self)

        self.create_edge(my_id, left_id,  "left")
        self.create_edge(my_id, right_id, "right")

        return my_id

    def visitUnaryOp(self, node):
        """
        UnaryOpNode: een unaire operatie met één operand.
        Geldt ook voor &x (address-of), *ptr (dereference),
        prefix++ en suffix++.

        DOT voorbeeld voor  -3 :
          n10 [label="UnaryOp: -"];
          n10 -- n11 [label="operand"];
        """
        my_id = self.new_id()
        self.create_node(my_id, f"UnaryOp: {node.op}")

        operand_id = node.operand.accept(self)
        self.create_edge(my_id, operand_id, "operand")

        return my_id

    def visitCast(self, node):
        """
        CastNode: een expliciete type cast.

        DOT voorbeeld voor  (int) x :
          n12 [label="Cast"];
          n12 -- n13 [label="to type"];
          n12 -- n14 [label="operand"];
        """
        my_id = self.new_id()
        self.create_node(my_id, "Cast")

        type_id    = node.target_type.accept(self)
        operand_id = node.operand.accept(self)

        self.create_edge(my_id, type_id,    "to type")
        self.create_edge(my_id, operand_id, "operand")

        return my_id