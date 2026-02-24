// --------------------
// Parser rules
// --------------------
file : (expression SC)* EOF ;
expression : expression (operator expression)* | '(' expression ')' | INTEGER;

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