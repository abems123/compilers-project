// Elke grammar file moet beginnen met de naam.
// De naam moet exact overeenkomen met de bestandsnaam!
grammar assignment_3;

// --------------------
// Parser rules
// --------------------

// ── NIEUW: #include <stdio.h> bovenaan het programma ────────────────────────
// We staan nul of meer includes toe vóór de main functie.
// We gebruiken het INCLUDE_STDIO token dat hieronder als één lexer regel
// gedefinieerd is, zodat we geen conflict krijgen met < en > operatoren.
program
    : includeStmt* INT_KW MAIN LPAREN RPAREN block EOF
    ;

includeStmt
    : INCLUDE_STDIO   // #include <stdio.h>
    ;

// Een statement is één van de volgende dingen:
//   - een variabele declaratie:       int x;  of  const float* p = &y;
//   - ── NIEUW: array declaratie:     int arr[3] = {1, 2, 3};
//   - een expressie statement:        x + 1;  of  x++;
//   - een assignment:                 x = 5;  of  *ptr = 3;
//   - ── NIEUW: function call stmt:   printf("hi");  scanf("%d", &x);
//   - ── NIEUW: een comment:          // tekst  of  /* tekst */
statement
    : varDec
    | arrayDec
    | varAss
    | functionCall SC
    | expression SC
    | comment
    ;

// Een blok is een reeks statements tussen accolades: { ... }
block
    : LBRACE (statement)* RBRACE
    ;

// Type: optioneel 'const', dan een basistype, dan nul of meer '*'
// Ongewijzigd ten opzichte van assignment 2.
type
    : CONST_KW? baseType STAR*
    ;

// De drie basistypen die ondersteund worden
baseType
    : INT_KW
    | FLOAT_KW
    | CHAR_KW
    ;

// Gewone variabele declaratie (ONGEWIJZIGD van assignment 2)
// Voorbeeld: int x;   of   float y = 3.14;   of   const int* p = &z;
varDec
    : type ID (ASSIGN expression)? SC
    ;

// ── NIEUW: Array declaratie ──────────────────────────────────────────────────
// Voorbeelden:
//   int arr[3];                              → 1D array, geen initialisatie
//   int arr[3] = {1, 2, 3};                 → 1D array, met initialisatie
//   int arr[2][4];                           → 2D array, geen initialisatie
//   int arr[2][3] = {{1,2,3},{4,5,6}};      → 2D array, met initialisatie
//
// We gebruiken (LBRACKET INTEGER RBRACKET)+ zodat 1D én multi-dimensionaal
// allemaal door dezelfde regel gedekt worden.
// De INTEGER in de dimensie mag alleen een positief getal zijn (geen expressie).
arrayDec
    : type ID (LBRACKET INTEGER RBRACKET)+ (ASSIGN arrayInit)? SC
    ;

// ── NIEUW: Array initialisator ────────────────────────────────────────────────
// Voorbeeld: {1, 2, 3}  of  {{1,2,3},{4,5,6}}
//
// arrayElement is ofwel een gewone expressie (voor 1D)
// of een geneste arrayInit (voor 2D en verder).
// De ? na de komma-lijst staat toe dat de initialisator leeg is: {}
arrayInit
    : LBRACE (arrayElement (COMMA arrayElement)*)? RBRACE
    ;

arrayElement
    : expression   // gewone waarde:   1, x+2, -9
    | arrayInit    // geneste rij:     {1, 2, 3}
    ;

// Assignment statement (ONGEWIJZIGD van assignment 2)
// expression ASSIGN expression zodat *ptr = 5 ook werkt.
varAss
    : expression ASSIGN expression SC
    ;

// ── NIEUW: Function call statement ───────────────────────────────────────────
// Ondersteunt printf en scanf (en in principe elke functieaanroep).
//
// Voorbeelden:
//   printf("hello\n");
//   printf("Number: %d", x);
//   scanf("%d", &x);
//
// De argumentenlijst is optioneel (een functie zonder argumenten is ook geldig).
// We gebruiken (expression (COMMA expression)*)? voor nul of meer argumenten.
functionCall
    : ID LPAREN (expression (COMMA expression)*)? RPAREN
    ;

// ── NIEUW: Comment als statement ─────────────────────────────────────────────
// In plaats van comments te skippen, maken we ze een echte grammar regel.
// Zo worden ze opgeslagen in de AST en kunnen ze later in de LLVM output
// komen als ; commentaar.
//
// LINE_COMMENT_TOKEN  → // dit is een comment
// BLOCK_COMMENT_TOKEN → /* dit is
//                          een multi-line comment */
comment
    : LINE_COMMENT_TOKEN
    | BLOCK_COMMENT_TOKEN
    ;

// Expressies (uitgebreid met array toegang en string literals)
expression
    : expression STAR        expression   // vermenigvuldiging:       3 * 4
    | expression SLASH       expression   // deling:                  6 / 2
    | expression PERCENT     expression   // modulo:                  7 % 3
    | expression PLUS        expression   // optelling:               3 + 4
    | expression MINUS       expression   // aftrekking:              5 - 1
    | expression LSHIFT      expression   // shift left:              x << 2
    | expression RSHIFT      expression   // shift right:             x >> 1
    | expression LT          expression   // kleiner dan:             x < 5
    | expression LEQ         expression   // kleiner of gelijk:       x <= 5
    | expression GT          expression   // groter dan:              x > 5
    | expression GEQ         expression   // groter of gelijk:        x >= 5
    | expression EQ          expression   // gelijk aan:              x == 5
    | expression NOTEQ       expression   // niet gelijk aan:         x != 5
    | expression AND         expression   // bitwise AND:             x & y
    | expression HAT         expression   // bitwise XOR:             x ^ y
    | expression OR          expression   // bitwise OR:              x | y
    | expression ANDAND      expression   // logische AND:            x && y
    | expression OROR        expression   // logische OR:             x || y
    | expression PLUSPLUS                 // suffix ++:               x++
    | expression MINUSMINUS              // suffix --:               x--
    // ── NIEUW: Array toegang ─────────────────────────────────────────────────
    // arr[i]    → expression LBRACKET expression RBRACKET
    // arr[i][j] → dit werkt automatisch door links-recursie:
    //             (arr[i])[j] = expression[j]
    | expression LBRACKET expression RBRACKET  // array toegang: arr[i]
    // ── NIEUW: function call als expressie (return waarde gebruiken) ─────────
    // int n = printf("hello");
    | functionCall
    | MINUS      expression               // unaire min:              -3
    | PLUS       expression               // unaire plus:             +3
    | EXMARK     expression               // logische NOT:            !x
    | TILDE      expression               // bitwise NOT:             ~x
    | AND        expression               // address-of:              &x
    | STAR       expression               // pointer dereference:     *ptr
    | PLUSPLUS   expression               // prefix ++:               ++x
    | MINUSMINUS expression               // prefix --:               --x
    | LPAREN type RPAREN expression       // cast:                    (int) x
    | LPAREN expression RPAREN            // haakjes:                 (3 + 4)
    | INTEGER                             // integer literal:         42
    | FLOAT                              // float literal:           3.14
    | ID                                  // variabele:               x
    | CHAR                               // char literal:            'a'
    // ── NIEUW: String literal ────────────────────────────────────────────────
    // "hello"  →  STRING token
    | STRING                              // string literal:          "hello"
    ;

// --------------------
// Lexer rules
// --------------------
// VOLGORDE IS BELANGRIJK:
//   1. Langere / specifiekere tokens VOOR kortere / algemenere
//   2. Keywords VOOR ID
// --------------------

// Whitespace: spaties, tabs, newlines → overslaan
WS : [ \n\t\r]+ -> skip ;

// ── NIEUW: Comments als tokens (niet meer skippen!) ─────────────────────────
// We sturen ze naar kanaal HIDDEN zodat de parser ze niet ziet
// (de parser zou struikelen over comments midden in expressies),
// maar ze zijn WEL beschikbaar via de token stream voor de visitor.
//
// WACHT — we gebruiken ze als statement-alternatieven (zie boven),
// dus ze mogen NIET naar HIDDEN. Ze moeten gewone tokens zijn.
//
// Echter: comments kunnen OVERAL staan, ook midden in code die we al
// hebben. Daarom: we sturen ze naar HIDDEN zodat de parser ze niet
// als verplicht onderdeel van de grammatica ziet, maar ze zijn
// opvraagbaar via ctx.start.tokenSource.
//
// KEUZE HIER: we maken ze gewone tokens (geen hidden, geen skip).
// De grammar regel 'comment' zorgt dat ze alleen op statement-niveau
// geldig zijn. Midden in een expressie zijn ze dan een syntax error —
// dat is acceptabel voor ons compiler project.
LINE_COMMENT_TOKEN  : '//' ~[\r\n]*              ;   // // dit is een comment
// BELANGRIJK: '/*' .*? '*/' werkt NIET voor multi-line comments omdat
// '.' in ANTLR geen newlines matcht. We gebruiken (~'*' | '*'+ ~[*/])*
// — dit is het standaard patroon voor C block comments:
//   - ~'*'         : elk karakter dat geen '*' is (inclusief newlines)
//   - '*'+ ~[*/]   : één of meer '*' gevolgd door iets dat geen '/' of '*' is
// Zo matchen we ook: /* dit is\neen\nmulti-line\ncomment */
BLOCK_COMMENT_TOKEN : '/*' (~'*' | '*'+ ~[*/])* '*'+ '/'  ;   // /* multi-line */

// ── NIEUW: #include <stdio.h> als één enkel token ───────────────────────────
// We matchen de hele include-regel als één token zodat we geen conflict
// krijgen met de < en > operatoren in expressies.
// [ \t]* staat spaties/tabs toe tussen de onderdelen.
INCLUDE_STDIO : '#' [ \t]* 'include' [ \t]* '<stdio.h>' ;

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
CHAR : '\'' ( '\\' [btnfr'\\] | ~['\\\r\n] ) '\'' ;

// ── NIEUW: String literal ─────────────────────────────────────────────────────
// "hello"   → gewone string
// "hi\n"    → string met escape sequence
// "x: %d"  → format string voor printf
//
// Toegestane escape sequences: \n \t \r \\ \"
// %% wordt NIET door de lexer afgehandeld — dat is printf's eigen logica
STRING : '"' ( '\\' [ntr"\\] | ~["\\\r\n] )* '"' ;

// Identifier: begint met letter of underscore
// Staat NA keywords zodat 'int' niet als ID herkend wordt!
ID : [a-zA-Z_][a-zA-Z0-9_]* ;

// Twee-karakter operatoren EERST
PLUSPLUS   : '++' ;
MINUSMINUS : '--' ;
OROR       : '||' ;
ANDAND     : '&&' ;
EQ         : '==' ;
NOTEQ      : '!=' ;
LEQ        : '<=' ;
GEQ        : '>=' ;
LSHIFT     : '<<' ;
RSHIFT     : '>>' ;

// Één-karakter operatoren
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
LPAREN   : '(' ;
RPAREN   : ')' ;
SC       : ';' ;
LBRACE   : '{' ;
RBRACE   : '}' ;
// ── NIEUW: vierkante haakjes en komma voor arrays ───────────────────────────
LBRACKET : '[' ;
RBRACKET : ']' ;
COMMA    : ',' ;