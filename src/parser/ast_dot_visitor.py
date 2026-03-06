# src/parser/ast_dot_visitor.py

class ASTDotVisitor:
    """
    Bezoekt alle AST nodes en genereert Graphviz DOT formaat.

    Assignment 3 voegt toe:
      - visitProgram    : toont nu ook de includes als kinderen
      - visitInclude    : blad node voor #include <stdio.h>
      - visitArrayDecl  : array declaratie met dimensies
      - visitArrayInit  : { ... } initialisator
      - visitArrayAccess: arr[i] toegang
      - visitStringLiteral: "hello" string
      - visitFunctionCall : printf(...) / scanf(...)
      - visitComment    : // of /* */ comment

    BUGFIX t.o.v. assignment 2:
      create_node escapet nu ook \\n in labels, zodat multi-line
      block comments geen kapotte DOT output geven.
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
        """
        Schrijft een DOT node definitie: n1 [label="..."];

        EDGE CASE: labels kunnen deze problematische tekens bevatten:
          - "  → crasht DOT parser  → escapen als \"
          - \\n → zorgt voor meerdere regels in DOT → escapen als \\\\n
          - \\t → tabs in labels     → escapen als \\\\t
          - \\  → backslash          → escapen als \\\\

        VOLGORDE IS BELANGRIJK: eerst backslashes escapen, dan pas
        de andere tekens. Anders worden eerder geëscapete backslashes
        dubbel geëscaped.
        """
        # stap 1: backslashes eerst (anders worden \\ dubbel geëscaped)
        safe = label.replace('\\', '\\\\')
        # stap 2: aanhalingstekens
        safe = safe.replace('"', '\\"')
        # stap 3: newlines (komen voor in multi-line block comments)
        safe = safe.replace('\n', '\\n')
        # stap 4: tabs
        safe = safe.replace('\t', '\\t')

        self.lines.append(f'  {node_id} [label="{safe}"];')

    def create_edge(self, src, dst, edge_label=None):
        """Schrijft een DOT edge: n1 -- n2;  of  n1 -- n2 [label="..."];"""
        if edge_label is None:
            self.lines.append(f"  {src} -- {dst};")
        else:
            # edge labels kunnen ook " bevatten → escapen
            safe_label = edge_label.replace('"', '\\"')
            self.lines.append(f'  {src} -- {dst} [label="{safe_label}"];')

    def finalize(self):
        """Sluit de DOT graph af en geeft de volledige string terug."""
        self.lines.append("}")
        return "\n".join(self.lines)

    # ============================================================
    # STRUCTUUR NODES
    # ============================================================

    def visitProgram(self, node):
        """
        ProgramNode (assignment 5): toont alle globals in volgorde.

        Elk global item (include, define, enum, funcDecl, funcDef, varDecl)
        wordt als genummerd kind getoond met een edge-label die het type aangeeft.
        """
        my_id = self.new_id()
        self.create_node(my_id, "Program")

        for i, item in enumerate(node.globals):
            item_id = item.accept(self)
            self.create_edge(my_id, item_id, f"[{i}]")

        return my_id

    def visitBlock(self, node):
        """
        BlockNode: een blok van statements { ... }.

        EDGE CASE: lege block {} → geen statement kinderen,
        maar de node zelf wordt wel getekend.
        """
        my_id = self.new_id()
        self.create_node(my_id, "Block")

        for i, stmt in enumerate(node.statements):
            stmt_id = stmt.accept(self)
            self.create_edge(my_id, stmt_id, f"stmt[{i}]")

        return my_id

    # ============================================================
    # INCLUDE NODE (NIEUW)
    # ============================================================

    def visitInclude(self, node):
        """
        IncludeNode: een blad node voor #include <stdio.h>.

        DOT voorbeeld:
          n2 [label="#include <stdio.h>"];
        """
        my_id = self.new_id()
        self.create_node(my_id, f"#include <{node.header}>")
        return my_id

    # ============================================================
    # DECLARATIE EN ASSIGNMENT NODES (ongewijzigd + ArrayDecl)
    # ============================================================

    def visitVarDecl(self, node):
        """
        VarDeclNode: variabele declaratie.
        Ongewijzigd van assignment 2.
        """
        my_id = self.new_id()
        type_str = repr(node.var_type).replace("TypeNode(", "").rstrip(")")
        self.create_node(my_id, f"VarDecl: {node.name}\\n{type_str}")

        type_id = node.var_type.accept(self)
        self.create_edge(my_id, type_id, "type")

        if node.value is not None:
            value_id = node.value.accept(self)
            self.create_edge(my_id, value_id, "init")

        return my_id

    def visitArrayDecl(self, node):
        """
        ArrayDeclNode: array declaratie.

        We tonen de dimensies direct in het label voor leesbaarheid.

        DOT voorbeeld voor  int matrix[2][3] :
          n3 [label="ArrayDecl: matrix\\nint[2][3]"];
          n3 -- n4 [label="type"];
          n3 -- n5 [label="init"];   ← alleen als er initialisatie is

        EDGE CASE: node.dimensions is altijd een niet-lege lijst
        (de grammar dwingt minstens één dimensie af).
        """
        my_id = self.new_id()

        # bouw een leesbaar label: naam + type + dimensies
        dims_str = ''.join(f'[{d}]' for d in node.dimensions)
        type_str = node.var_type.base_type
        self.create_node(my_id, f"ArrayDecl: {node.name}\\n{type_str}{dims_str}")

        # teken de TypeNode als kind
        type_id = node.var_type.accept(self)
        self.create_edge(my_id, type_id, "type")

        # teken de initialisator als die er is
        if node.initializer is not None:
            init_id = node.initializer.accept(self)
            self.create_edge(my_id, init_id, "init")

        return my_id

    def visitAssign(self, node):
        """
        AssignNode: assignment statement.
        Ongewijzigd van assignment 2.
        """
        my_id = self.new_id()
        self.create_node(my_id, "Assign")

        target_id = node.target.accept(self)
        self.create_edge(my_id, target_id, "target")

        value_id = node.value.accept(self)
        self.create_edge(my_id, value_id, "value")

        return my_id

    # ============================================================
    # TYPE NODE (ongewijzigd)
    # ============================================================

    def visitType(self, node):
        """
        TypeNode: een type zoals int, const float*, int**.
        Ongewijzigd van assignment 2.
        """
        my_id = self.new_id()
        const_str = "const " if node.is_const else ""
        stars     = "*" * node.pointer_depth
        self.create_node(my_id, f"Type: {const_str}{node.base_type}{stars}")
        return my_id

    # ============================================================
    # ARRAY NODES (NIEUW)
    # ============================================================

    def visitArrayInit(self, node):
        """
        ArrayInitNode: een initialisator { ... }.

        Elk element wordt als genummerd kind getoond.

        EDGE CASE: lege initialisator {} → geen kinderen,
        maar het label toont "(leeg)" voor duidelijkheid.

        DOT voorbeeld voor  {1, 2, 3} :
          n5 [label="ArrayInit"];
          n5 -- n6 [label="[0]"];
          n5 -- n7 [label="[1]"];
          n5 -- n8 [label="[2]"];

        DOT voorbeeld voor  {} :
          n5 [label="ArrayInit (leeg)"];
        """
        my_id = self.new_id()

        if len(node.elements) == 0:
            self.create_node(my_id, "ArrayInit (leeg)")
        else:
            self.create_node(my_id, "ArrayInit")
            for i, elem in enumerate(node.elements):
                elem_id = elem.accept(self)
                self.create_edge(my_id, elem_id, f"[{i}]")

        return my_id

    def visitArrayAccess(self, node):
        """
        ArrayAccessNode: array toegang arr[i].

        EDGE CASE: voor arr[i][j] is de array_expr zelf een ArrayAccessNode.
        Dit geeft een geneste boom:
          ArrayAccess
            ├── array: ArrayAccess
            │     ├── array: Var(arr)
            │     └── index: Var(i)
            └── index: Var(j)

        DOT voorbeeld voor  arr[i] :
          n9  [label="ArrayAccess"];
          n9  -- n10 [label="array"];
          n9  -- n11 [label="index"];
        """
        my_id = self.new_id()
        self.create_node(my_id, "ArrayAccess")

        array_id = node.array_expr.accept(self)
        self.create_edge(my_id, array_id, "array")

        index_id = node.index.accept(self)
        self.create_edge(my_id, index_id, "index")

        return my_id

    # ============================================================
    # EXPRESSIE NODES
    # ============================================================

    def visitLiteral(self, node):
        """
        LiteralNode: een concrete waarde.
        Ongewijzigd van assignment 2.
        """
        my_id = self.new_id()
        self.create_node(my_id, f"Literal: {node.value!r} ({node.type_name})")
        return my_id

    def visitStringLiteral(self, node):
        """
        StringLiteralNode: een string literal "...".

        EDGE CASE: de string kan aanhalingstekens, backslashes en newlines
        bevatten. create_node escapet dit correct.

        DOT voorbeeld voor  "hello\\n" :
          n12 [label="String: \\"hello\\\\n\\""];

        EDGE CASE: lege string "" → label = 'String: ""'
        """
        my_id = self.new_id()
        # We tonen de string met aanhalingstekens in het label voor duidelijkheid.
        # create_node zorgt voor de escaping.
        self.create_node(my_id, f'String: "{node.value}"')
        return my_id

    def visitVariable(self, node):
        """
        VariableNode: een identifier.
        Ongewijzigd van assignment 2.
        """
        my_id = self.new_id()
        self.create_node(my_id, f"Var: {node.name}")
        return my_id

    def visitBinaryOp(self, node):
        """
        BinaryOpNode: een binaire operatie.
        Ongewijzigd van assignment 2.
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
        UnaryOpNode: een unaire operatie.
        Ongewijzigd van assignment 2.
        """
        my_id = self.new_id()
        self.create_node(my_id, f"UnaryOp: {node.op}")

        operand_id = node.operand.accept(self)
        self.create_edge(my_id, operand_id, "operand")

        return my_id

    def visitCast(self, node):
        """
        CastNode: een expliciete type cast.
        Ongewijzigd van assignment 2.
        """
        my_id = self.new_id()
        self.create_node(my_id, "Cast")

        type_id    = node.target_type.accept(self)
        operand_id = node.operand.accept(self)

        self.create_edge(my_id, type_id,    "to type")
        self.create_edge(my_id, operand_id, "operand")

        return my_id

    # ============================================================
    # FUNCTIE AANROEP (NIEUW)
    # ============================================================

    def visitFunctionCall(self, node):
        """
        FunctionCallNode: printf(...) of scanf(...).

        De naam staat in het label. De argumenten worden als
        genummerde kinderen getoond.

        EDGE CASE: geen argumenten → geen kinderen, label toont
        de naam met lege haakjes voor duidelijkheid.

        DOT voorbeeld voor  printf("hello\\n", x) :
          n13 [label="Call: printf"];
          n13 -- n14 [label="arg[0]"];
          n13 -- n15 [label="arg[1]"];

        DOT voorbeeld voor  printf() :
          n13 [label="Call: printf (geen args)"];
        """
        my_id = self.new_id()

        if len(node.args) == 0:
            self.create_node(my_id, f"Call: {node.name} (geen args)")
        else:
            self.create_node(my_id, f"Call: {node.name}")
            for i, arg in enumerate(node.args):
                arg_id = arg.accept(self)
                self.create_edge(my_id, arg_id, f"arg[{i}]")

        return my_id

    # ============================================================
    # COMMENT NODE (NIEUW)
    # ============================================================

    def visitComment(self, node):
        """
        CommentNode: een comment die bewaard is in de AST.

        We tonen een preview van maximaal 30 tekens in het label,
        zodat lange multi-line comments de DOT visualisatie niet
        onleesbaar maken.

        EDGE CASE: multi-line comments bevatten \\n → create_node
        escapet dit correct naar \\\\n in het DOT label.

        EDGE CASE: lege comment "//" → preview = "//"

        DOT voorbeeld voor  // dit is een comment :
          n16 [label="Comment: // dit is een comm..."];

        DOT voorbeeld voor  /* multi\\nline */ :
          n16 [label="Comment: /* multi\\\\nline */"];
        """
        my_id = self.new_id()

        # preview: maximaal 30 tekens van de comment tekst
        preview = node.text[:30]
        suffix  = "..." if len(node.text) > 30 else ""

        self.create_node(my_id, f"Comment: {preview}{suffix}")
        return my_id

    # ============================================================
    # ASSIGNMENT 4 — ENUM, CONTROL FLOW, SCOPE
    # ============================================================

    def visitEnumDef(self, node):
        """enum Status { READY, BUSY } → labels als kommalijst in het label."""
        my_id = self.new_id()
        labels_str = ', '.join(node.labels)
        self.create_node(my_id, f"EnumDef: {node.name}\n{{{labels_str}}}")
        return my_id

    def visitIf(self, node):
        my_id = self.new_id()
        self.create_node(my_id, "If")

        cond_id = node.condition.accept(self)
        self.create_edge(my_id, cond_id, "condition")

        then_id = node.then_block.accept(self)
        self.create_edge(my_id, then_id, "then")

        if node.else_block is not None:
            else_id = node.else_block.accept(self)
            self.create_edge(my_id, else_id, "else")

        return my_id

    def visitWhile(self, node):
        my_id = self.new_id()
        self.create_node(my_id, "While")

        cond_id = node.condition.accept(self)
        self.create_edge(my_id, cond_id, "condition")

        body_id = node.body.accept(self)
        self.create_edge(my_id, body_id, "body")

        return my_id

    def visitBreak(self, node):
        my_id = self.new_id()
        self.create_node(my_id, "Break")
        return my_id

    def visitContinue(self, node):
        my_id = self.new_id()
        self.create_node(my_id, "Continue")
        return my_id

    def visitScope(self, node):
        my_id = self.new_id()
        self.create_node(my_id, "Scope")
        body_id = node.body.accept(self)
        self.create_edge(my_id, body_id, "body")
        return my_id

    # ============================================================
    # ASSIGNMENT 5 — PREPROCESSOR NODES
    # ============================================================

    def visitIncludeFile(self, node):
        """#include "pad/naar/file.h" → blad node."""
        my_id = self.new_id()
        self.create_node(my_id, f'#include "{node.path}"')
        return my_id

    def visitDefine(self, node):
        """#define naam waarde → blad node met naam en waarde."""
        my_id = self.new_id()
        value_str = f" = {node.value}" if node.value else ""
        self.create_node(my_id, f"#define {node.name}{value_str}")
        return my_id

    # ============================================================
    # ASSIGNMENT 5 — FUNCTIE NODES
    # ============================================================

    def visitParam(self, node):
        """Één parameter: type + naam als blad node."""
        my_id = self.new_id()
        const_str = "const " if node.param_type.is_const else ""
        stars     = "*" * node.param_type.pointer_depth
        self.create_node(my_id, f"Param: {const_str}{node.param_type.base_type}{stars} {node.name}")
        return my_id

    def visitFunctionDecl(self, node):
        """
        Forward declaration: return type + naam + parameters.

        DOT voorbeeld voor  int mul(int x, int y); :
          n5 [label="FuncDecl: int mul"];
          n5 -- n6 [label="param[0]"];
          n5 -- n7 [label="param[1]"];
        """
        my_id = self.new_id()
        ret_str = f"{node.return_type.base_type}{'*' * node.return_type.pointer_depth}"
        self.create_node(my_id, f"FuncDecl: {ret_str} {node.name}")

        for i, param in enumerate(node.params):
            param_id = param.accept(self)
            self.create_edge(my_id, param_id, f"param[{i}]")

        return my_id

    def visitFunctionDef(self, node):
        """
        Functiedefinitie: return type + naam + parameters + body.

        DOT voorbeeld voor  int mul(int x, int y) { ... } :
          n5 [label="FuncDef: int mul"];
          n5 -- n6 [label="param[0]"];
          n5 -- n7 [label="param[1]"];
          n5 -- n8 [label="body"];
        """
        my_id = self.new_id()
        ret_str = f"{node.return_type.base_type}{'*' * node.return_type.pointer_depth}"
        self.create_node(my_id, f"FuncDef: {ret_str} {node.name}")

        for i, param in enumerate(node.params):
            param_id = param.accept(self)
            self.create_edge(my_id, param_id, f"param[{i}]")

        body_id = node.body.accept(self)
        self.create_edge(my_id, body_id, "body")

        return my_id

    def visitReturn(self, node):
        """
        Return statement.
          return x + 1; → ReturnNode met waarde als kind
          return;       → blad node
        """
        my_id = self.new_id()
        self.create_node(my_id, "Return")

        if node.value is not None:
            val_id = node.value.accept(self)
            self.create_edge(my_id, val_id, "value")

        return my_id