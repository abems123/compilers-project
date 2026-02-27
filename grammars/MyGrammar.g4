// --------------------
// Parser rules
// --------------------
grammar MyGrammar;

program : (expression SC)* EOF ;
expression : expression PLUS expression | 
             expression MINUS expression | 
             expression STAR expression | 
             expression SLASH expression | 
             L_PARENTHESIS expression R_PARENTHESIS | 
             INTEGER;


// --------------------
// Lexer rules
// --------------------
WS: [ \n\t\r]+ -> skip;
fragment DIGIT : [0-9];
INTEGER : DIGIT+;
PLUS : '+';
MINUS : '-';
STAR : '*';
SLASH : '/';
PERCENT : '%';
L_PARENTHESIS : '(';
R_PARENTHESIS : ')';
OR : '|';
OROR : '||';
AND : '&';
ANDAND : '&&';
EXMARK : '!';
LEQ : '<=';
GEQ : '>=';
NOTEQ : '!=';
LSHIFT : '<<';
RSHIFT : '>>';
TILDE : '~';
HAT : '^';
SC : ';';