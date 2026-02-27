// Elke grammar file moet beginnen met de naam.
// De naam moet exact overeenkomen met de bestandsnaam!
grammar assignment_1;

// --------------------
// Parser rules
// --------------------
// Parser regels zijn in lowercase geschreven.
// Ze beschrijven de STRUCTUUR van de input.
// --------------------

// Een file is een lijst van expressies, elk gevolgd door een puntkomma.
// De * betekent: nul of meer keer.
// EOF betekent: einde van het bestand.
program : (expression SC)* EOF ;

// Een expressie kan drie dingen zijn:
//
// 1. Een binaire operatie: expression operator expression
//    Voorbeeld: 3 + 4, 5 * 2
//
// 2. Een unaire operatie: unaire_operator expression
//    Voorbeeld: -3, !5, ~7
//    We schrijven de operatoren hier direct omdat ANTLR
//    dan beter weet welke tokens hij verwacht.
//
// 3. Haakjes: ( expression )
//    Voorbeeld: (3 + 4)
//
// 4. Een getal: INTEGER
//    Voorbeeld: 3, 42, 0
//
// BELANGRIJK: de volgorde hier bepaalt de prioriteit!
// ANTLR lost ambiguïteit op door de eerste regel te kiezen.
// Maar voor operator-prioriteit (bv. * voor +) gebruiken
// we later aparte regels als dat nodig is.

expression
    : expression STAR     expression   // vermenigvuldiging
    | expression SLASH    expression   // deling
    | expression PERCENT  expression   // modulo
    | expression PLUS     expression   // optelling
    | expression MINUS    expression   // aftrekking
    | expression LSHIFT   expression   // shift left
    | expression RSHIFT   expression   // shift right
    | expression LT       expression   // kleiner dan
    | expression LEQ      expression   // kleiner dan of gelijk
    | expression GT       expression   // groter dan
    | expression GEQ      expression   // groter dan of gelijk
    | expression EQ       expression   // gelijk aan
    | expression NOTEQ    expression   // niet gelijk aan
    | expression AND      expression   // bitwise AND
    | expression HAT      expression   // bitwise XOR
    | expression OR       expression   // bitwise OR
    | expression ANDAND   expression   // logische AND
    | expression OROR     expression   // logische OR
    | MINUS     expression             // unaire min:     -3
    | PLUS      expression             // unaire plus:    +3
    | EXMARK    expression             // logische NOT:   !3
    | TILDE     expression             // bitwise NOT:    ~3
    | LPAREN expression RPAREN         // haakjes:        (3 + 4)
    | INTEGER                          // getal:          42
    ;

// --------------------
// Lexer rules
// --------------------
// Lexer regels zijn in UPPERCASE geschreven.
// Ze beschrijven hoe de input wordt opgesplitst in tokens.
//
// BELANGRIJK: langere tokens ALTIJD voor kortere!
// Anders leest ANTLR '||' als twee '|' tokens.
// --------------------

// Whitespace: spaties, tabs, newlines → gewoon overslaan
WS : [ \n\t\r]+ -> skip ;

// Getal: één of meer cijfers
// fragment betekent: dit is een hulpregel, geen token op zich
fragment DIGIT : [0-9] ;
INTEGER : DIGIT+ ;

// Twee-karakter operatoren EERST (voor de één-karakter versies!)
OROR   : '||' ;   // logische OR     (voor OR)
ANDAND : '&&' ;   // logische AND    (voor AND)
EQ     : '==' ;   // gelijk aan
NOTEQ  : '!=' ;   // niet gelijk aan (voor EXMARK)
LEQ    : '<=' ;   // kleiner of gelijk (voor LT en LSHIFT)
GEQ    : '>=' ;   // groter of gelijk  (voor GT en RSHIFT)
LSHIFT : '<<' ;   // shift left        (voor LT)
RSHIFT : '>>' ;   // shift right       (voor GT)

// Één-karakter operatoren DAARNA
PLUS    : '+' ;
MINUS   : '-' ;
STAR    : '*' ;
SLASH   : '/' ;
PERCENT : '%' ;
AND     : '&' ;
OR      : '|' ;
HAT     : '^' ;
TILDE   : '~' ;
EXMARK  : '!' ;
LT      : '<' ;
GT      : '>' ;

// Haakjes en puntkomma
LPAREN : '(' ;
RPAREN : ')' ;
SC     : ';' ;