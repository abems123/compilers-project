# Generated from example_source_files/MyGrammar.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .MyGrammarParser import MyGrammarParser
else:
    from MyGrammarParser import MyGrammarParser

# This class defines a complete generic visitor for a parse tree produced by MyGrammarParser.

class MyGrammarVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MyGrammarParser#program.
    def visitProgram(self, ctx:MyGrammarParser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#statement.
    def visitStatement(self, ctx:MyGrammarParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#block.
    def visitBlock(self, ctx:MyGrammarParser.BlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#varDecl.
    def visitVarDecl(self, ctx:MyGrammarParser.VarDeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#assignStmt.
    def visitAssignStmt(self, ctx:MyGrammarParser.AssignStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#printStmt.
    def visitPrintStmt(self, ctx:MyGrammarParser.PrintStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#ifStmt.
    def visitIfStmt(self, ctx:MyGrammarParser.IfStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#whileStmt.
    def visitWhileStmt(self, ctx:MyGrammarParser.WhileStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#expr.
    def visitExpr(self, ctx:MyGrammarParser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#orExpr.
    def visitOrExpr(self, ctx:MyGrammarParser.OrExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#andExpr.
    def visitAndExpr(self, ctx:MyGrammarParser.AndExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#equalityExpr.
    def visitEqualityExpr(self, ctx:MyGrammarParser.EqualityExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#compareExpr.
    def visitCompareExpr(self, ctx:MyGrammarParser.CompareExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#addExpr.
    def visitAddExpr(self, ctx:MyGrammarParser.AddExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#mulExpr.
    def visitMulExpr(self, ctx:MyGrammarParser.MulExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#unaryExpr.
    def visitUnaryExpr(self, ctx:MyGrammarParser.UnaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MyGrammarParser#primary.
    def visitPrimary(self, ctx:MyGrammarParser.PrimaryContext):
        return self.visitChildren(ctx)



del MyGrammarParser