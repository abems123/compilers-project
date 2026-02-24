# Generated from example_source_files/MyGrammar.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .MyGrammarParser import MyGrammarParser
else:
    from MyGrammarParser import MyGrammarParser

# This class defines a complete listener for a parse tree produced by MyGrammarParser.
class MyGrammarListener(ParseTreeListener):

    # Enter a parse tree produced by MyGrammarParser#program.
    def enterProgram(self, ctx:MyGrammarParser.ProgramContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#program.
    def exitProgram(self, ctx:MyGrammarParser.ProgramContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#statement.
    def enterStatement(self, ctx:MyGrammarParser.StatementContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#statement.
    def exitStatement(self, ctx:MyGrammarParser.StatementContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#block.
    def enterBlock(self, ctx:MyGrammarParser.BlockContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#block.
    def exitBlock(self, ctx:MyGrammarParser.BlockContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#varDecl.
    def enterVarDecl(self, ctx:MyGrammarParser.VarDeclContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#varDecl.
    def exitVarDecl(self, ctx:MyGrammarParser.VarDeclContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#assignStmt.
    def enterAssignStmt(self, ctx:MyGrammarParser.AssignStmtContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#assignStmt.
    def exitAssignStmt(self, ctx:MyGrammarParser.AssignStmtContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#printStmt.
    def enterPrintStmt(self, ctx:MyGrammarParser.PrintStmtContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#printStmt.
    def exitPrintStmt(self, ctx:MyGrammarParser.PrintStmtContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#ifStmt.
    def enterIfStmt(self, ctx:MyGrammarParser.IfStmtContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#ifStmt.
    def exitIfStmt(self, ctx:MyGrammarParser.IfStmtContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#whileStmt.
    def enterWhileStmt(self, ctx:MyGrammarParser.WhileStmtContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#whileStmt.
    def exitWhileStmt(self, ctx:MyGrammarParser.WhileStmtContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#expr.
    def enterExpr(self, ctx:MyGrammarParser.ExprContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#expr.
    def exitExpr(self, ctx:MyGrammarParser.ExprContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#orExpr.
    def enterOrExpr(self, ctx:MyGrammarParser.OrExprContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#orExpr.
    def exitOrExpr(self, ctx:MyGrammarParser.OrExprContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#andExpr.
    def enterAndExpr(self, ctx:MyGrammarParser.AndExprContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#andExpr.
    def exitAndExpr(self, ctx:MyGrammarParser.AndExprContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#equalityExpr.
    def enterEqualityExpr(self, ctx:MyGrammarParser.EqualityExprContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#equalityExpr.
    def exitEqualityExpr(self, ctx:MyGrammarParser.EqualityExprContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#compareExpr.
    def enterCompareExpr(self, ctx:MyGrammarParser.CompareExprContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#compareExpr.
    def exitCompareExpr(self, ctx:MyGrammarParser.CompareExprContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#addExpr.
    def enterAddExpr(self, ctx:MyGrammarParser.AddExprContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#addExpr.
    def exitAddExpr(self, ctx:MyGrammarParser.AddExprContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#mulExpr.
    def enterMulExpr(self, ctx:MyGrammarParser.MulExprContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#mulExpr.
    def exitMulExpr(self, ctx:MyGrammarParser.MulExprContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#unaryExpr.
    def enterUnaryExpr(self, ctx:MyGrammarParser.UnaryExprContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#unaryExpr.
    def exitUnaryExpr(self, ctx:MyGrammarParser.UnaryExprContext):
        pass


    # Enter a parse tree produced by MyGrammarParser#primary.
    def enterPrimary(self, ctx:MyGrammarParser.PrimaryContext):
        pass

    # Exit a parse tree produced by MyGrammarParser#primary.
    def exitPrimary(self, ctx:MyGrammarParser.PrimaryContext):
        pass



del MyGrammarParser