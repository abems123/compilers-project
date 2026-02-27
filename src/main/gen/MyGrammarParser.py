# Generated from grammars/MyGrammar.g4 by ANTLR 4.13.2
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
        4,1,22,40,2,0,7,0,2,1,7,1,1,0,1,0,1,0,5,0,8,8,0,10,0,12,0,11,9,0,
        1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,1,3,1,21,8,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,5,1,35,8,1,10,1,12,1,38,9,1,1,1,0,1,2,
        2,0,2,0,0,43,0,9,1,0,0,0,2,20,1,0,0,0,4,5,3,2,1,0,5,6,5,22,0,0,6,
        8,1,0,0,0,7,4,1,0,0,0,8,11,1,0,0,0,9,7,1,0,0,0,9,10,1,0,0,0,10,12,
        1,0,0,0,11,9,1,0,0,0,12,13,5,0,0,1,13,1,1,0,0,0,14,15,6,1,-1,0,15,
        16,5,8,0,0,16,17,3,2,1,0,17,18,5,9,0,0,18,21,1,0,0,0,19,21,5,2,0,
        0,20,14,1,0,0,0,20,19,1,0,0,0,21,36,1,0,0,0,22,23,10,6,0,0,23,24,
        5,3,0,0,24,35,3,2,1,7,25,26,10,5,0,0,26,27,5,4,0,0,27,35,3,2,1,6,
        28,29,10,4,0,0,29,30,5,5,0,0,30,35,3,2,1,5,31,32,10,3,0,0,32,33,
        5,6,0,0,33,35,3,2,1,4,34,22,1,0,0,0,34,25,1,0,0,0,34,28,1,0,0,0,
        34,31,1,0,0,0,35,38,1,0,0,0,36,34,1,0,0,0,36,37,1,0,0,0,37,3,1,0,
        0,0,38,36,1,0,0,0,4,9,20,34,36
    ]

class MyGrammarParser ( Parser ):

    grammarFileName = "MyGrammar.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "'+'", "'-'", 
                     "'*'", "'/'", "'%'", "'('", "')'", "'|'", "'||'", "'&'", 
                     "'&&'", "'!'", "'<='", "'>='", "'!='", "'<<'", "'>>'", 
                     "'~'", "'^'", "';'" ]

    symbolicNames = [ "<INVALID>", "WS", "INTEGER", "PLUS", "MINUS", "STAR", 
                      "SLASH", "PERCENT", "L_PARENTHESIS", "R_PARENTHESIS", 
                      "OR", "OROR", "AND", "ANDAND", "EXMARK", "LEQ", "GEQ", 
                      "NOTEQ", "LSHIFT", "RSHIFT", "TILDE", "HAT", "SC" ]

    RULE_program = 0
    RULE_expression = 1

    ruleNames =  [ "program", "expression" ]

    EOF = Token.EOF
    WS=1
    INTEGER=2
    PLUS=3
    MINUS=4
    STAR=5
    SLASH=6
    PERCENT=7
    L_PARENTHESIS=8
    R_PARENTHESIS=9
    OR=10
    OROR=11
    AND=12
    ANDAND=13
    EXMARK=14
    LEQ=15
    GEQ=16
    NOTEQ=17
    LSHIFT=18
    RSHIFT=19
    TILDE=20
    HAT=21
    SC=22

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

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.ExpressionContext,i)


        def SC(self, i:int=None):
            if i is None:
                return self.getTokens(MyGrammarParser.SC)
            else:
                return self.getToken(MyGrammarParser.SC, i)

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
            self.state = 9
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==2 or _la==8:
                self.state = 4
                self.expression(0)
                self.state = 5
                self.match(MyGrammarParser.SC)
                self.state = 11
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 12
            self.match(MyGrammarParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def L_PARENTHESIS(self):
            return self.getToken(MyGrammarParser.L_PARENTHESIS, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(MyGrammarParser.ExpressionContext)
            else:
                return self.getTypedRuleContext(MyGrammarParser.ExpressionContext,i)


        def R_PARENTHESIS(self):
            return self.getToken(MyGrammarParser.R_PARENTHESIS, 0)

        def INTEGER(self):
            return self.getToken(MyGrammarParser.INTEGER, 0)

        def PLUS(self):
            return self.getToken(MyGrammarParser.PLUS, 0)

        def MINUS(self):
            return self.getToken(MyGrammarParser.MINUS, 0)

        def STAR(self):
            return self.getToken(MyGrammarParser.STAR, 0)

        def SLASH(self):
            return self.getToken(MyGrammarParser.SLASH, 0)

        def getRuleIndex(self):
            return MyGrammarParser.RULE_expression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression" ):
                listener.enterExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression" ):
                listener.exitExpression(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExpression" ):
                return visitor.visitExpression(self)
            else:
                return visitor.visitChildren(self)



    def expression(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = MyGrammarParser.ExpressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 2
        self.enterRecursionRule(localctx, 2, self.RULE_expression, _p)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 20
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [8]:
                self.state = 15
                self.match(MyGrammarParser.L_PARENTHESIS)
                self.state = 16
                self.expression(0)
                self.state = 17
                self.match(MyGrammarParser.R_PARENTHESIS)
                pass
            elif token in [2]:
                self.state = 19
                self.match(MyGrammarParser.INTEGER)
                pass
            else:
                raise NoViableAltException(self)

            self._ctx.stop = self._input.LT(-1)
            self.state = 36
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,3,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 34
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
                    if la_ == 1:
                        localctx = MyGrammarParser.ExpressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 22
                        if not self.precpred(self._ctx, 6):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 6)")
                        self.state = 23
                        self.match(MyGrammarParser.PLUS)
                        self.state = 24
                        self.expression(7)
                        pass

                    elif la_ == 2:
                        localctx = MyGrammarParser.ExpressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 25
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 26
                        self.match(MyGrammarParser.MINUS)
                        self.state = 27
                        self.expression(6)
                        pass

                    elif la_ == 3:
                        localctx = MyGrammarParser.ExpressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 28
                        if not self.precpred(self._ctx, 4):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 4)")
                        self.state = 29
                        self.match(MyGrammarParser.STAR)
                        self.state = 30
                        self.expression(5)
                        pass

                    elif la_ == 4:
                        localctx = MyGrammarParser.ExpressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 31
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 32
                        self.match(MyGrammarParser.SLASH)
                        self.state = 33
                        self.expression(4)
                        pass

             
                self.state = 38
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[1] = self.expression_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expression_sempred(self, localctx:ExpressionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 6)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 5)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 4)
         

            if predIndex == 3:
                return self.precpred(self._ctx, 3)
         




