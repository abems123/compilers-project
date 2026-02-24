# Generated from example_source_files/MyGrammar.g4 by ANTLR 4.13.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,30,159,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,1,0,5,0,36,8,0,10,0,12,0,39,9,0,1,
        0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,3,1,49,8,1,1,2,1,2,5,2,53,8,2,10,2,
        12,2,56,9,2,1,2,1,2,1,3,1,3,1,3,1,3,3,3,64,8,3,1,3,1,3,1,4,1,4,1,
        4,1,4,1,4,1,5,1,5,1,5,1,5,1,5,1,5,1,6,1,6,1,6,1,6,1,6,1,6,1,6,3,
        6,86,8,6,1,7,1,7,1,7,1,7,1,7,1,7,1,8,1,8,1,9,1,9,1,9,5,9,99,8,9,
        10,9,12,9,102,9,9,1,10,1,10,1,10,5,10,107,8,10,10,10,12,10,110,9,
        10,1,11,1,11,1,11,5,11,115,8,11,10,11,12,11,118,9,11,1,12,1,12,1,
        12,5,12,123,8,12,10,12,12,12,126,9,12,1,13,1,13,1,13,5,13,131,8,
        13,10,13,12,13,134,9,13,1,14,1,14,1,14,5,14,139,8,14,10,14,12,14,
        142,9,14,1,15,1,15,1,15,3,15,147,8,15,1,16,1,16,1,16,1,16,1,16,1,
        16,1,16,1,16,3,16,157,8,16,1,16,0,0,17,0,2,4,6,8,10,12,14,16,18,
        20,22,24,26,28,30,32,0,5,1,0,8,9,1,0,10,13,1,0,15,16,1,0,17,18,2,
        0,16,16,19,19,161,0,37,1,0,0,0,2,48,1,0,0,0,4,50,1,0,0,0,6,59,1,
        0,0,0,8,67,1,0,0,0,10,72,1,0,0,0,12,78,1,0,0,0,14,87,1,0,0,0,16,
        93,1,0,0,0,18,95,1,0,0,0,20,103,1,0,0,0,22,111,1,0,0,0,24,119,1,
        0,0,0,26,127,1,0,0,0,28,135,1,0,0,0,30,146,1,0,0,0,32,156,1,0,0,
        0,34,36,3,2,1,0,35,34,1,0,0,0,36,39,1,0,0,0,37,35,1,0,0,0,37,38,
        1,0,0,0,38,40,1,0,0,0,39,37,1,0,0,0,40,41,5,0,0,1,41,1,1,0,0,0,42,
        49,3,6,3,0,43,49,3,8,4,0,44,49,3,10,5,0,45,49,3,12,6,0,46,49,3,14,
        7,0,47,49,3,4,2,0,48,42,1,0,0,0,48,43,1,0,0,0,48,44,1,0,0,0,48,45,
        1,0,0,0,48,46,1,0,0,0,48,47,1,0,0,0,49,3,1,0,0,0,50,54,5,22,0,0,
        51,53,3,2,1,0,52,51,1,0,0,0,53,56,1,0,0,0,54,52,1,0,0,0,54,55,1,
        0,0,0,55,57,1,0,0,0,56,54,1,0,0,0,57,58,5,23,0,0,58,5,1,0,0,0,59,
        60,5,1,0,0,60,63,5,28,0,0,61,62,5,14,0,0,62,64,3,16,8,0,63,61,1,
        0,0,0,63,64,1,0,0,0,64,65,1,0,0,0,65,66,5,24,0,0,66,7,1,0,0,0,67,
        68,5,28,0,0,68,69,5,14,0,0,69,70,3,16,8,0,70,71,5,24,0,0,71,9,1,
        0,0,0,72,73,5,5,0,0,73,74,5,20,0,0,74,75,3,16,8,0,75,76,5,21,0,0,
        76,77,5,24,0,0,77,11,1,0,0,0,78,79,5,2,0,0,79,80,5,20,0,0,80,81,
        3,16,8,0,81,82,5,21,0,0,82,85,3,4,2,0,83,84,5,3,0,0,84,86,3,4,2,
        0,85,83,1,0,0,0,85,86,1,0,0,0,86,13,1,0,0,0,87,88,5,4,0,0,88,89,
        5,20,0,0,89,90,3,16,8,0,90,91,5,21,0,0,91,92,3,4,2,0,92,15,1,0,0,
        0,93,94,3,18,9,0,94,17,1,0,0,0,95,100,3,20,10,0,96,97,5,6,0,0,97,
        99,3,20,10,0,98,96,1,0,0,0,99,102,1,0,0,0,100,98,1,0,0,0,100,101,
        1,0,0,0,101,19,1,0,0,0,102,100,1,0,0,0,103,108,3,22,11,0,104,105,
        5,7,0,0,105,107,3,22,11,0,106,104,1,0,0,0,107,110,1,0,0,0,108,106,
        1,0,0,0,108,109,1,0,0,0,109,21,1,0,0,0,110,108,1,0,0,0,111,116,3,
        24,12,0,112,113,7,0,0,0,113,115,3,24,12,0,114,112,1,0,0,0,115,118,
        1,0,0,0,116,114,1,0,0,0,116,117,1,0,0,0,117,23,1,0,0,0,118,116,1,
        0,0,0,119,124,3,26,13,0,120,121,7,1,0,0,121,123,3,26,13,0,122,120,
        1,0,0,0,123,126,1,0,0,0,124,122,1,0,0,0,124,125,1,0,0,0,125,25,1,
        0,0,0,126,124,1,0,0,0,127,132,3,28,14,0,128,129,7,2,0,0,129,131,
        3,28,14,0,130,128,1,0,0,0,131,134,1,0,0,0,132,130,1,0,0,0,132,133,
        1,0,0,0,133,27,1,0,0,0,134,132,1,0,0,0,135,140,3,30,15,0,136,137,
        7,3,0,0,137,139,3,30,15,0,138,136,1,0,0,0,139,142,1,0,0,0,140,138,
        1,0,0,0,140,141,1,0,0,0,141,29,1,0,0,0,142,140,1,0,0,0,143,144,7,
        4,0,0,144,147,3,30,15,0,145,147,3,32,16,0,146,143,1,0,0,0,146,145,
        1,0,0,0,147,31,1,0,0,0,148,157,5,26,0,0,149,157,5,25,0,0,150,157,
        5,27,0,0,151,157,5,28,0,0,152,153,5,20,0,0,153,154,3,16,8,0,154,
        155,5,21,0,0,155,157,1,0,0,0,156,148,1,0,0,0,156,149,1,0,0,0,156,
        150,1,0,0,0,156,151,1,0,0,0,156,152,1,0,0,0,157,33,1,0,0,0,13,37,
        48,54,63,85,100,108,116,124,132,140,146,156
    ]

class MyGrammarParser ( Parser ):

    grammarFileName = "MyGrammar.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'let'", "'if'", "'else'", "'while'", 
                     "'print'", "'||'", "'&&'", "'=='", "'!='", "'<='", 
                     "'>='", "'<'", "'>'", "'='", "'+'", "'-'", "'*'", "'/'", 
                     "'!'", "'('", "')'", "'{'", "'}'", "';'" ]

    symbolicNames = [ "<INVALID>", "LET", "IF", "ELSE", "WHILE", "PRINT", 
                      "OR", "AND", "EQ", "NEQ", "LTE", "GTE", "LT", "GT", 
                      "ASSIGN", "PLUS", "MINUS", "STAR", "SLASH", "NOT", 
                      "LPAREN", "RPAREN", "LBRACE", "RBRACE", "SEMI", "BOOL", 
                      "INT", "STRING", "ID", "WS", "LINE_COMMENT" ]

    RULE_program = 0
    RULE_statement = 1
    RULE_block = 2
    RULE_varDecl = 3
    RULE_assignStmt = 4
    RULE_printStmt = 5
    RULE_ifStmt = 6
    RULE_whileStmt = 7
    RULE_expr = 8
    RULE_orExpr = 9
    RULE_andExpr = 10
    RULE_equalityExpr = 11
    RULE_compareExpr = 12
    RULE_addExpr = 13
    RULE_mulExpr = 14
    RULE_unaryExpr = 15
    RULE_primary = 16

    ruleNames =  [ "program", "statement", "block", "varDecl", "assignStmt", 
                   "printStmt", "ifStmt", "whileStmt", "expr", "orExpr", 
                   "andExpr", "equalityExpr", "compareExpr", "addExpr", 
                   "mulExpr", "unaryExpr", "primary" ]

    EOF = Token.EOF
    LET=1
    IF=2
    ELSE=3
    WHILE=4
    PRINT=5
    OR=6
    AND=7
    EQ=8
    NEQ=9
    LTE=10
    GTE=11
    LT=12
    GT=13
    ASSIGN=14
    PLUS=15
    MINUS=16
    STAR=17
    SLASH=18
    NOT=19
    LPAREN=20
    RPAREN=21
    LBRACE=22
    RBRACE=23
    SEMI=24
    BOOL=25
    INT=26
    STRING=27
    ID=28
    WS=29
    LINE_COMMENT=30

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(MyGrammarParser.EOF, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.StatementContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.StatementContext,i)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitProgram" ):
                return visitor.visitProgram(self)
            else:
                return visitor.visitChildren(self)




    def program(self):

        localctx = MyGrammarParser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 37
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 272629814) != 0):
                self.state = 34
                self.statement()
                self.state = 39
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 40
            self.match(MyGrammarParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def varDecl(self):
            return self.getTypedRuleContext(MyGrammarParser.VarDeclContext,0)


        def assignStmt(self):
            return self.getTypedRuleContext(MyGrammarParser.AssignStmtContext,0)


        def printStmt(self):
            return self.getTypedRuleContext(MyGrammarParser.PrintStmtContext,0)


        def ifStmt(self):
            return self.getTypedRuleContext(MyGrammarParser.IfStmtContext,0)


        def whileStmt(self):
            return self.getTypedRuleContext(MyGrammarParser.WhileStmtContext,0)


        def block(self):
            return self.getTypedRuleContext(MyGrammarParser.BlockContext,0)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement" ):
                listener.enterStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement" ):
                listener.exitStatement(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitStatement" ):
                return visitor.visitStatement(self)
            else:
                return visitor.visitChildren(self)




    def statement(self):

        localctx = MyGrammarParser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_statement)
        try:
            self.state = 48
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [1]:
                self.enterOuterAlt(localctx, 1)
                self.state = 42
                self.varDecl()
                pass
            elif token in [28]:
                self.enterOuterAlt(localctx, 2)
                self.state = 43
                self.assignStmt()
                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 3)
                self.state = 44
                self.printStmt()
                pass
            elif token in [2]:
                self.enterOuterAlt(localctx, 4)
                self.state = 45
                self.ifStmt()
                pass
            elif token in [4]:
                self.enterOuterAlt(localctx, 5)
                self.state = 46
                self.whileStmt()
                pass
            elif token in [22]:
                self.enterOuterAlt(localctx, 6)
                self.state = 47
                self.block()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BlockContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(MyGrammarParser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(MyGrammarParser.RBRACE, 0)

        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.StatementContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.StatementContext,i)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_block

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBlock" ):
                listener.enterBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBlock" ):
                listener.exitBlock(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBlock" ):
                return visitor.visitBlock(self)
            else:
                return visitor.visitChildren(self)




    def block(self):

        localctx = MyGrammarParser.BlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_block)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 50
            self.match(MyGrammarParser.LBRACE)
            self.state = 54
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 272629814) != 0):
                self.state = 51
                self.statement()
                self.state = 56
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 57
            self.match(MyGrammarParser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VarDeclContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LET(self):
            return self.getToken(MyGrammarParser.LET, 0)

        def ID(self):
            return self.getToken(MyGrammarParser.ID, 0)

        def SEMI(self):
            return self.getToken(MyGrammarParser.SEMI, 0)

        def ASSIGN(self):
            return self.getToken(MyGrammarParser.ASSIGN, 0)

        def expr(self):
            return self.getTypedRuleContext(MyGrammarParser.ExprContext,0)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_varDecl

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVarDecl" ):
                listener.enterVarDecl(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVarDecl" ):
                listener.exitVarDecl(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVarDecl" ):
                return visitor.visitVarDecl(self)
            else:
                return visitor.visitChildren(self)




    def varDecl(self):

        localctx = MyGrammarParser.VarDeclContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_varDecl)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 59
            self.match(MyGrammarParser.LET)
            self.state = 60
            self.match(MyGrammarParser.ID)
            self.state = 63
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==14:
                self.state = 61
                self.match(MyGrammarParser.ASSIGN)
                self.state = 62
                self.expr()


            self.state = 65
            self.match(MyGrammarParser.SEMI)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssignStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ID(self):
            return self.getToken(MyGrammarParser.ID, 0)

        def ASSIGN(self):
            return self.getToken(MyGrammarParser.ASSIGN, 0)

        def expr(self):
            return self.getTypedRuleContext(MyGrammarParser.ExprContext,0)


        def SEMI(self):
            return self.getToken(MyGrammarParser.SEMI, 0)

        def getRuleIndex(self):
            return MyGrammarParser.RULE_assignStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAssignStmt" ):
                listener.enterAssignStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAssignStmt" ):
                listener.exitAssignStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAssignStmt" ):
                return visitor.visitAssignStmt(self)
            else:
                return visitor.visitChildren(self)




    def assignStmt(self):

        localctx = MyGrammarParser.AssignStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_assignStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 67
            self.match(MyGrammarParser.ID)
            self.state = 68
            self.match(MyGrammarParser.ASSIGN)
            self.state = 69
            self.expr()
            self.state = 70
            self.match(MyGrammarParser.SEMI)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PrintStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def PRINT(self):
            return self.getToken(MyGrammarParser.PRINT, 0)

        def LPAREN(self):
            return self.getToken(MyGrammarParser.LPAREN, 0)

        def expr(self):
            return self.getTypedRuleContext(MyGrammarParser.ExprContext,0)


        def RPAREN(self):
            return self.getToken(MyGrammarParser.RPAREN, 0)

        def SEMI(self):
            return self.getToken(MyGrammarParser.SEMI, 0)

        def getRuleIndex(self):
            return MyGrammarParser.RULE_printStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrintStmt" ):
                listener.enterPrintStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrintStmt" ):
                listener.exitPrintStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrintStmt" ):
                return visitor.visitPrintStmt(self)
            else:
                return visitor.visitChildren(self)




    def printStmt(self):

        localctx = MyGrammarParser.PrintStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_printStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 72
            self.match(MyGrammarParser.PRINT)
            self.state = 73
            self.match(MyGrammarParser.LPAREN)
            self.state = 74
            self.expr()
            self.state = 75
            self.match(MyGrammarParser.RPAREN)
            self.state = 76
            self.match(MyGrammarParser.SEMI)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IfStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IF(self):
            return self.getToken(MyGrammarParser.IF, 0)

        def LPAREN(self):
            return self.getToken(MyGrammarParser.LPAREN, 0)

        def expr(self):
            return self.getTypedRuleContext(MyGrammarParser.ExprContext,0)


        def RPAREN(self):
            return self.getToken(MyGrammarParser.RPAREN, 0)

        def block(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.BlockContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.BlockContext,i)


        def ELSE(self):
            return self.getToken(MyGrammarParser.ELSE, 0)

        def getRuleIndex(self):
            return MyGrammarParser.RULE_ifStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIfStmt" ):
                listener.enterIfStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIfStmt" ):
                listener.exitIfStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIfStmt" ):
                return visitor.visitIfStmt(self)
            else:
                return visitor.visitChildren(self)




    def ifStmt(self):

        localctx = MyGrammarParser.IfStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_ifStmt)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 78
            self.match(MyGrammarParser.IF)
            self.state = 79
            self.match(MyGrammarParser.LPAREN)
            self.state = 80
            self.expr()
            self.state = 81
            self.match(MyGrammarParser.RPAREN)
            self.state = 82
            self.block()
            self.state = 85
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==3:
                self.state = 83
                self.match(MyGrammarParser.ELSE)
                self.state = 84
                self.block()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class WhileStmtContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHILE(self):
            return self.getToken(MyGrammarParser.WHILE, 0)

        def LPAREN(self):
            return self.getToken(MyGrammarParser.LPAREN, 0)

        def expr(self):
            return self.getTypedRuleContext(MyGrammarParser.ExprContext,0)


        def RPAREN(self):
            return self.getToken(MyGrammarParser.RPAREN, 0)

        def block(self):
            return self.getTypedRuleContext(MyGrammarParser.BlockContext,0)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_whileStmt

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterWhileStmt" ):
                listener.enterWhileStmt(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitWhileStmt" ):
                listener.exitWhileStmt(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitWhileStmt" ):
                return visitor.visitWhileStmt(self)
            else:
                return visitor.visitChildren(self)




    def whileStmt(self):

        localctx = MyGrammarParser.WhileStmtContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_whileStmt)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 87
            self.match(MyGrammarParser.WHILE)
            self.state = 88
            self.match(MyGrammarParser.LPAREN)
            self.state = 89
            self.expr()
            self.state = 90
            self.match(MyGrammarParser.RPAREN)
            self.state = 91
            self.block()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def orExpr(self):
            return self.getTypedRuleContext(MyGrammarParser.OrExprContext,0)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_expr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpr" ):
                listener.enterExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpr" ):
                listener.exitExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExpr" ):
                return visitor.visitExpr(self)
            else:
                return visitor.visitChildren(self)




    def expr(self):

        localctx = MyGrammarParser.ExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_expr)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 93
            self.orExpr()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class OrExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def andExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.AndExprContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.AndExprContext,i)


        def OR(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.OR)
            else:
                return self.getToken(MyGrammarParser.OR, i)

        def getRuleIndex(self):
            return MyGrammarParser.RULE_orExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterOrExpr" ):
                listener.enterOrExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitOrExpr" ):
                listener.exitOrExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitOrExpr" ):
                return visitor.visitOrExpr(self)
            else:
                return visitor.visitChildren(self)




    def orExpr(self):

        localctx = MyGrammarParser.OrExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_orExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 95
            self.andExpr()
            self.state = 100
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==6:
                self.state = 96
                self.match(MyGrammarParser.OR)
                self.state = 97
                self.andExpr()
                self.state = 102
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AndExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def equalityExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.EqualityExprContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.EqualityExprContext,i)


        def AND(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.AND)
            else:
                return self.getToken(MyGrammarParser.AND, i)

        def getRuleIndex(self):
            return MyGrammarParser.RULE_andExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAndExpr" ):
                listener.enterAndExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAndExpr" ):
                listener.exitAndExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAndExpr" ):
                return visitor.visitAndExpr(self)
            else:
                return visitor.visitChildren(self)




    def andExpr(self):

        localctx = MyGrammarParser.AndExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_andExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 103
            self.equalityExpr()
            self.state = 108
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==7:
                self.state = 104
                self.match(MyGrammarParser.AND)
                self.state = 105
                self.equalityExpr()
                self.state = 110
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EqualityExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def compareExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.CompareExprContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.CompareExprContext,i)


        def EQ(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.EQ)
            else:
                return self.getToken(MyGrammarParser.EQ, i)

        def NEQ(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.NEQ)
            else:
                return self.getToken(MyGrammarParser.NEQ, i)

        def getRuleIndex(self):
            return MyGrammarParser.RULE_equalityExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEqualityExpr" ):
                listener.enterEqualityExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEqualityExpr" ):
                listener.exitEqualityExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEqualityExpr" ):
                return visitor.visitEqualityExpr(self)
            else:
                return visitor.visitChildren(self)




    def equalityExpr(self):

        localctx = MyGrammarParser.EqualityExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_equalityExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 111
            self.compareExpr()
            self.state = 116
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==8 or _la==9:
                self.state = 112
                _la = self._input.LA(1)
                if not(_la==8 or _la==9):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 113
                self.compareExpr()
                self.state = 118
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CompareExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def addExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.AddExprContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.AddExprContext,i)


        def LT(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.LT)
            else:
                return self.getToken(MyGrammarParser.LT, i)

        def LTE(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.LTE)
            else:
                return self.getToken(MyGrammarParser.LTE, i)

        def GT(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.GT)
            else:
                return self.getToken(MyGrammarParser.GT, i)

        def GTE(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.GTE)
            else:
                return self.getToken(MyGrammarParser.GTE, i)

        def getRuleIndex(self):
            return MyGrammarParser.RULE_compareExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCompareExpr" ):
                listener.enterCompareExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCompareExpr" ):
                listener.exitCompareExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCompareExpr" ):
                return visitor.visitCompareExpr(self)
            else:
                return visitor.visitChildren(self)




    def compareExpr(self):

        localctx = MyGrammarParser.CompareExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_compareExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 119
            self.addExpr()
            self.state = 124
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & 15360) != 0):
                self.state = 120
                _la = self._input.LA(1)
                if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 15360) != 0)):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 121
                self.addExpr()
                self.state = 126
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AddExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def mulExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.MulExprContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.MulExprContext,i)


        def PLUS(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.PLUS)
            else:
                return self.getToken(MyGrammarParser.PLUS, i)

        def MINUS(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.MINUS)
            else:
                return self.getToken(MyGrammarParser.MINUS, i)

        def getRuleIndex(self):
            return MyGrammarParser.RULE_addExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAddExpr" ):
                listener.enterAddExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAddExpr" ):
                listener.exitAddExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitAddExpr" ):
                return visitor.visitAddExpr(self)
            else:
                return visitor.visitChildren(self)




    def addExpr(self):

        localctx = MyGrammarParser.AddExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_addExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 127
            self.mulExpr()
            self.state = 132
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==15 or _la==16:
                self.state = 128
                _la = self._input.LA(1)
                if not(_la==15 or _la==16):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 129
                self.mulExpr()
                self.state = 134
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MulExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def unaryExpr(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.UnaryExprContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.UnaryExprContext,i)


        def STAR(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.STAR)
            else:
                return self.getToken(MyGrammarParser.STAR, i)

        def SLASH(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.SLASH)
            else:
                return self.getToken(MyGrammarParser.SLASH, i)

        def getRuleIndex(self):
            return MyGrammarParser.RULE_mulExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMulExpr" ):
                listener.enterMulExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMulExpr" ):
                listener.exitMulExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMulExpr" ):
                return visitor.visitMulExpr(self)
            else:
                return visitor.visitChildren(self)




    def mulExpr(self):

        localctx = MyGrammarParser.MulExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_mulExpr)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 135
            self.unaryExpr()
            self.state = 140
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==17 or _la==18:
                self.state = 136
                _la = self._input.LA(1)
                if not(_la==17 or _la==18):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 137
                self.unaryExpr()
                self.state = 142
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class UnaryExprContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def unaryExpr(self):
            return self.getTypedRuleContext(MyGrammarParser.UnaryExprContext,0)


        def NOT(self):
            return self.getToken(MyGrammarParser.NOT, 0)

        def MINUS(self):
            return self.getToken(MyGrammarParser.MINUS, 0)

        def primary(self):
            return self.getTypedRuleContext(MyGrammarParser.PrimaryContext,0)


        def getRuleIndex(self):
            return MyGrammarParser.RULE_unaryExpr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUnaryExpr" ):
                listener.enterUnaryExpr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUnaryExpr" ):
                listener.exitUnaryExpr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitUnaryExpr" ):
                return visitor.visitUnaryExpr(self)
            else:
                return visitor.visitChildren(self)




    def unaryExpr(self):

        localctx = MyGrammarParser.UnaryExprContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_unaryExpr)
        self._la = 0 # Token type
        try:
            self.state = 146
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [16, 19]:
                self.enterOuterAlt(localctx, 1)
                self.state = 143
                _la = self._input.LA(1)
                if not(_la==16 or _la==19):
                    self._errHandler.recoverInline(self)
                else:
                    self._errHandler.reportMatch(self)
                    self.consume()
                self.state = 144
                self.unaryExpr()
                pass
            elif token in [20, 25, 26, 27, 28]:
                self.enterOuterAlt(localctx, 2)
                self.state = 145
                self.primary()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PrimaryContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INT(self):
            return self.getToken(MyGrammarParser.INT, 0)

        def BOOL(self):
            return self.getToken(MyGrammarParser.BOOL, 0)

        def STRING(self):
            return self.getToken(MyGrammarParser.STRING, 0)

        def ID(self):
            return self.getToken(MyGrammarParser.ID, 0)

        def LPAREN(self):
            return self.getToken(MyGrammarParser.LPAREN, 0)

        def expr(self):
            return self.getTypedRuleContext(MyGrammarParser.ExprContext,0)


        def RPAREN(self):
            return self.getToken(MyGrammarParser.RPAREN, 0)

        def getRuleIndex(self):
            return MyGrammarParser.RULE_primary

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPrimary" ):
                listener.enterPrimary(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPrimary" ):
                listener.exitPrimary(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPrimary" ):
                return visitor.visitPrimary(self)
            else:
                return visitor.visitChildren(self)




    def primary(self):

        localctx = MyGrammarParser.PrimaryContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_primary)
        try:
            self.state = 156
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [26]:
                self.enterOuterAlt(localctx, 1)
                self.state = 148
                self.match(MyGrammarParser.INT)
                pass
            elif token in [25]:
                self.enterOuterAlt(localctx, 2)
                self.state = 149
                self.match(MyGrammarParser.BOOL)
                pass
            elif token in [27]:
                self.enterOuterAlt(localctx, 3)
                self.state = 150
                self.match(MyGrammarParser.STRING)
                pass
            elif token in [28]:
                self.enterOuterAlt(localctx, 4)
                self.state = 151
                self.match(MyGrammarParser.ID)
                pass
            elif token in [20]:
                self.enterOuterAlt(localctx, 5)
                self.state = 152
                self.match(MyGrammarParser.LPAREN)
                self.state = 153
                self.expr()
                self.state = 154
                self.match(MyGrammarParser.RPAREN)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





