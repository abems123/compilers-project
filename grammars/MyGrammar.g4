// Elke grammar file moet beginnen met de naam.
// De naam moet exact overeenkomen met de bestandsnaam!
grammar MyGrammar;

// --------------------
// Parser rules
// --------------------
// Parser regels zijn in lowercase geschreven.
// Ze beschrijven de STRUCTUUR van de input.
// --------------------

// Het programma is altijd een int main() { ... } functie.
// Een ontbrekende main geeft een parse error.
program : INT_KW MAIN LPAREN RPAREN block EOF;

// Een statement is één van de volgende dingen:
//   - een variabele declaratie:   int x;  of  const float* p = &y;
//   - een expressie statement:    x + 1;  of  x++;
//   - een assignment:             x = 5;  of  *ptr = 3;
statement
    : varDec
    | expression SC
    | varAss
    ;

// Een blok is een reeks statements tussen accolades: { ... }
block
    : LBRACE (statement)* RBRACE
    ;

// Type: optioneel 'const', dan een basistype, dan nul of meer '*'
// Voorbeelden:
//   int        → gewone int
//   const int  → constante int
//   int*       → pointer naar int
//   const int* → pointer naar constante int
//   int**      → pointer naar pointer naar int
type
    : CONST_KW? baseType STAR*
    ;

// De drie basistypen die ondersteund worden
baseType
    : INT_KW
    | FLOAT_KW
    | CHAR_KW
    ;

// Variabele declaratie: type naam (optioneel = expressie) ;
// Voorbeelden:
//   int x;
//   float y = 3.14;
//   const int* p = &z;
//   int** pp;
varDec
    : type ID (ASSIGN expression)? SC
    ;

// Assignment statement: expressie = expressie ;
// We gebruiken expression aan de linkerkant zodat ook pointer
// dereferences werken: *ptr = 5;
// De semantische analyse zal later controleren of de linkerkant
// een geldige lvalue is (geen rvalue, geen const variabele).
varAss
    : expression ASSIGN expression SC
    ;

// Expressies, van laagste naar hoogste prioriteit.
// ANTLR lost ambiguïteit op via volgorde: eerste alternatief wint.
// Binaire operatoren zijn links-associatief door de recursie links.
expression
    : expression STAR        expression   // vermenigvuldiging:   3 * 4
    | expression SLASH       expression   // deling:              6 / 2
    | expression PERCENT     expression   // modulo:              7 % 3
    | expression PLUS        expression   // optelling:           3 + 4
    | expression MINUS       expression   // aftrekking:          5 - 1
    | expression LSHIFT      expression   // shift left:          x << 2
    | expression RSHIFT      expression   // shift right:         x >> 1
    | expression LT          expression   // kleiner dan:         x < 5
    | expression LEQ         expression   // kleiner of gelijk:   x <= 5
    | expression GT          expression   // groter dan:          x > 5
    | expression GEQ         expression   // groter of gelijk:    x >= 5
    | expression EQ          expression   // gelijk aan:          x == 5
    | expression NOTEQ       expression   // niet gelijk aan:     x != 5
    | expression AND         expression   // bitwise AND:         x & y
    | expression HAT         expression   // bitwise XOR:         x ^ y
    | expression OR          expression   // bitwise OR:          x | y
    | expression ANDAND      expression   // logische AND:        x && y
    | expression OROR        expression   // logische OR:         x || y
    | expression PLUSPLUS                 // suffix ++:           x++
    | expression MINUSMINUS               // suffix --:           x--
    | MINUS      expression               // unaire min:          -3
    | PLUS       expression               // unaire plus:         +3
    | EXMARK     expression               // logische NOT:        !x
    | TILDE      expression               // bitwise NOT:         ~x
    | AND        expression               // address-of:          &x
    | STAR       expression               // pointer dereference: *ptr
    | PLUSPLUS   expression               // prefix ++:           ++x
    | MINUSMINUS expression               // prefix --:           --x
    | LPAREN type RPAREN expression       // cast:                (int) x
    | LPAREN expression RPAREN            // haakjes:             (3 + 4)
    | INTEGER                             // integer literal:     42
    | FLOAT                               // float literal:       3.14
    | ID                                  // variabele:           x
    | CHAR                                // char literal:        'a'
    ;

// --------------------
// Lexer rules
// --------------------
// Lexer regels zijn in UPPERCASE geschreven.
// Ze beschrijven hoe de input wordt opgesplitst in tokens.
//
// VOLGORDE IS BELANGRIJK:
//   1. Keywords VOOR ID (anders wordt 'int' als ID herkend)
//   2. Langere tokens VOOR kortere (++ voor +, == voor =, enz.)
// --------------------

// Whitespace en comments: gewoon overslaan
WS           : [ \n\t\r]+    -> skip ;
LINE_COMMENT : '//' ~[\r\n]* -> skip ;

// Keywords (altijd VOOR de ID regel!)
INT_KW   : 'int'   ;
MAIN     : 'main'  ;
CONST_KW : 'const' ;
CHAR_KW  : 'char'  ;
FLOAT_KW : 'float' ;

// Literals
fragment DIGIT : [0-9] ;
INTEGER : DIGIT+ ;
FLOAT   : DIGIT+ '.' DIGIT+ ;

// Character literal: 'a', '\n', '\\', enz.
// '\\' [btnfr'\\] staat toe: \b \t \n \f \r \' \\
// ~['\\\r\n] staat toe: alles behalve ' \ en newline
CHAR : '\'' ( '\\' [btnfr'\\] | ~['\\\r\n] ) '\'' ;

// Identifier: begint met letter of underscore, dan letters/cijfers/underscore
// Staat NA keywords zodat 'int' niet als ID herkend wordt!
ID : [a-zA-Z_][a-zA-Z0-9_]* ;

// Twee-karakter operatoren EERST (voor de één-karakter versies!)
PLUSPLUS   : '++' ;   // voor PLUS
MINUSMINUS : '--' ;   // voor MINUS
OROR       : '||' ;   // voor OR
ANDAND     : '&&' ;   // voor AND
EQ         : '==' ;   // voor ASSIGN
NOTEQ      : '!=' ;   // voor EXMARK
LEQ        : '<=' ;   // voor LT en LSHIFT
GEQ        : '>=' ;   // voor GT en RSHIFT
LSHIFT     : '<<' ;   // voor LT
RSHIFT     : '>>' ;   // voor GT

// Één-karakter operatoren DAARNA
ASSIGN  : '='  ;
PLUS    : '+'  ;
MINUS   : '-'  ;
STAR    : '*'  ;
SLASH   : '/'  ;
PERCENT : '%'  ;
AND     : '&'  ;
OR      : '|'  ;
HAT     : '^'  ;
TILDE   : '~'  ;
EXMARK  : '!'  ;
LT      : '<'  ;
GT      : '>'  ;

// Interpunctie
LPAREN : '(' ;
RPAREN : ')' ;
SC     : ';' ;
LBRACE : '{' ;
RBRACE : '}' ;