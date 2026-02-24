// MiniLang.g4
grammar MyGrammar;

// --------------------
// Parser rules
// --------------------

program
  : statement* EOF
  ;

statement
  : varDecl
  | assignStmt
  | printStmt
  | ifStmt
  | whileStmt
  | block
  ;

block
  : LBRACE statement* RBRACE
  ;

varDecl
  : LET ID (ASSIGN expr)? SEMI
  ;

assignStmt
  : ID ASSIGN expr SEMI
  ;

printStmt
  : PRINT LPAREN expr RPAREN SEMI
  ;

ifStmt
  : IF LPAREN expr RPAREN block (ELSE block)?
  ;

whileStmt
  : WHILE LPAREN expr RPAREN block
  ;

// Expression with precedence (lowest -> highest)
expr        : orExpr ;
orExpr      : andExpr (OR andExpr)* ;
andExpr     : equalityExpr (AND equalityExpr)* ;
equalityExpr: compareExpr ((EQ | NEQ) compareExpr)* ;
compareExpr : addExpr ((LT | LTE | GT | GTE) addExpr)* ;
addExpr     : mulExpr ((PLUS | MINUS) mulExpr)* ;
mulExpr     : unaryExpr ((STAR | SLASH) unaryExpr)* ;
unaryExpr   : (NOT | MINUS) unaryExpr
            | primary
            ;

primary
  : INT
  | BOOL
  | STRING
  | ID
  | LPAREN expr RPAREN
  ;

// --------------------
// Lexer rules
// --------------------

// Keywords
LET   : 'let' ;
IF    : 'if' ;
ELSE  : 'else' ;
WHILE : 'while' ;
PRINT : 'print' ;

// Operators / punctuation
OR     : '||' ;
AND    : '&&' ;
EQ     : '==' ;
NEQ    : '!=' ;
LTE    : '<=' ;
GTE    : '>=' ;
LT     : '<' ;
GT     : '>' ;

ASSIGN : '=' ;
PLUS   : '+' ;
MINUS  : '-' ;
STAR   : '*' ;
SLASH  : '/' ;
NOT    : '!' ;

LPAREN : '(' ;
RPAREN : ')' ;
LBRACE : '{' ;
RBRACE : '}' ;
SEMI   : ';' ;

// Literals
INT    : [0-9]+ ;

// "hello", with basic escapes like \" and \\ and \n
STRING : '"' ( '\\' [btnfr"\\] | ~["\\] )* '"' ;

BOOL   : 'true' | 'false' ;

// Identifier (must come AFTER keywords so keywords match first)
ID     : [a-zA-Z_][a-zA-Z0-9_]* ;

// Skip whitespace and comments
WS           : [ \t\r\n]+ -> skip ;
LINE_COMMENT : '//' ~[\r\n]* -> skip ;