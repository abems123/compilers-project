# src/parser/dead_code_visitor.py
#
# Dead Code Elimination — Assignment 5 (verplicht).
#
# Verwijdert statements die nooit bereikt kunnen worden:
#   1. Statements NA een 'return' in een functie-body
#   2. Statements NA een 'break' of 'continue' in een loop/switch-body
#
# HOE WERKT HET?
#   We lopen door elke BlockNode en zodra we een ReturnNode, BreakNode
#   of ContinueNode tegenkomen, stoppen we met verdere statements
#   toe te voegen. Alles erna is dead code.
#
# EDGE CASES:
#   - return/break/continue in een geneste if of while → verwijdert NIET
#     de statements NA het if/while blok, want de if/while kan overgeslagen
#     worden. Alleen directe statements in hetzelfde blok worden verwijderd.
#   - Lege blokken na eliminatie → BlockNode([]) is geldig.
#   - De visitor geeft een NIEUWE AST terug (ongewijzigd patroon).

from .ast_nodes import (
    LiteralNode, BinaryOpNode, UnaryOpNode,
    VariableNode, VarDeclNode, AssignNode,
    CastNode, TypeNode, BlockNode, ProgramNode,
    CommentNode, ArrayDeclNode, ArrayInitNode,
    ArrayAccessNode, StringLiteralNode,
    FunctionCallNode, IncludeNode,
    EnumDefNode, IfNode, WhileNode,
    BreakNode, ContinueNode, ScopeNode,
    ParamNode, FunctionDeclNode, FunctionDefNode,
    ReturnNode, DefineNode, IncludeFileNode,
)


class DeadCodeVisitor:
    """
    Verwijdert onbereikbare statements na return/break/continue.

    Gebruik:
        visitor = DeadCodeVisitor()
        clean_ast = ast.accept(visitor)
    """

    # ── STRUCTUUR ──────────────────────────────────────────────────────────────

    def visitProgram(self, node):
        new_globals = [item.accept(self) for item in node.globals]
        return ProgramNode(new_globals)

    def visitBlock(self, node):
        """
        Kernlogica: loop door de statements en stop zodra we een
        ReturnNode, BreakNode of ContinueNode tegenkomen.

        EDGE CASE: de stopper-node zelf BLIJFT in de lijst — we verwijderen
        alleen de statements DAARNA.

        EDGE CASE: comments vóór een return blijven bewaard.
        EDGE CASE: meerdere returns in hetzelfde blok (via if/else) →
        we stoppen pas als er een directe return/break/continue is,
        niet als die in een geneste if zit.
        """
        new_statements = []
        for stmt in node.statements:
            new_stmt = stmt.accept(self)
            new_statements.append(new_stmt)

            # stopper gevonden? stop met verdere statements verwerken
            if isinstance(new_stmt, (ReturnNode, BreakNode, ContinueNode)):
                break   # ← alles erna is dead code

        return BlockNode(new_statements)

    # ── ASSIGNMENT 5: FUNCTIE NODES ───────────────────────────────────────────

    def visitFunctionDef(self, node):
        """Bezoek de body zodat dead code daarin verwijderd wordt."""
        new_body = node.body.accept(self)
        return FunctionDefNode(node.return_type, node.name, node.params, new_body)

    def visitFunctionDecl(self, node):
        return node  # forward declarations hebben geen body

    def visitReturn(self, node):
        """ReturnNode zelf bezoeken: verwerk de waarde-expressie."""
        if node.value is not None:
            new_value = node.value.accept(self)
        else:
            new_value = None
        return ReturnNode(new_value)

    def visitDefine(self, node):
        return node

    def visitIncludeFile(self, node):
        return node

    def visitParam(self, node):
        return node

    # ── CONTROL FLOW ──────────────────────────────────────────────────────────

    def visitIf(self, node):
        """
        Bezoek beide takken zodat dead code daarin verwijderd wordt.

        EDGE CASE: een return in de then-tak verwijdert NIET de statements
        na het if-statement — want de then-tak wordt misschien niet genomen.
        """
        new_condition  = node.condition.accept(self)
        new_then       = node.then_block.accept(self)
        new_else       = node.else_block.accept(self) if node.else_block else None
        return IfNode(new_condition, new_then, new_else)

    def visitWhile(self, node):
        """
        Bezoek de body. Break/continue in de body worden daar afgehandeld
        door visitBlock — de WhileNode zelf blijft intact.
        """
        new_condition = node.condition.accept(self)
        new_body      = node.body.accept(self)
        new_update    = node.update.accept(self) if node.update else None
        return WhileNode(new_condition, new_body, new_update)

    def visitBreak(self, node):
        return node  # blad-node, geen kinderen

    def visitContinue(self, node):
        return node  # blad-node, geen kinderen

    def visitScope(self, node):
        new_body = node.body.accept(self)
        return ScopeNode(new_body)

    # ── DECLARATIES EN ASSIGNMENTS ────────────────────────────────────────────

    def visitVarDecl(self, node):
        new_value = node.value.accept(self) if node.value else None
        return VarDeclNode(node.var_type, node.name, new_value)

    def visitArrayDecl(self, node):
        new_init = node.initializer.accept(self) if node.initializer else None
        return ArrayDeclNode(node.var_type, node.name, node.dimensions, new_init)

    def visitArrayInit(self, node):
        new_elements = [e.accept(self) for e in node.elements]
        return ArrayInitNode(new_elements)

    def visitAssign(self, node):
        new_target = node.target.accept(self)
        new_value  = node.value.accept(self)
        return AssignNode(new_target, new_value)

    # ── ENUMS ─────────────────────────────────────────────────────────────────

    def visitEnumDef(self, node):
        return node  # enum definities veranderen niet

    # ── EXPRESSIES (passthrough — geen dead code in expressies) ───────────────

    def visitLiteral(self, node):        return node
    def visitStringLiteral(self, node):  return node
    def visitVariable(self, node):       return node
    def visitComment(self, node):        return node
    def visitInclude(self, node):        return node
    def visitType(self, node):           return node

    def visitBinaryOp(self, node):
        return BinaryOpNode(node.op,
                            node.left.accept(self),
                            node.right.accept(self))

    def visitUnaryOp(self, node):
        return UnaryOpNode(node.op, node.operand.accept(self))

    def visitCast(self, node):
        return CastNode(node.target_type, node.operand.accept(self))

    def visitArrayAccess(self, node):
        return ArrayAccessNode(node.array_expr.accept(self),
                               node.index.accept(self))

    def visitFunctionCall(self, node):
        new_args = [arg.accept(self) for arg in node.args]
        return FunctionCallNode(node.name, new_args)