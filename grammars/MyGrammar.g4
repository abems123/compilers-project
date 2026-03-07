// Elke grammar file moet beginnen met de naam.
// De naam moet exact overeenkomen met de bestandsnaam!
grammar MyGrammar;

// --------------------
// Parser rules
// --------------------

// ── UITGEBREID: program ondersteunt nu globale functies, forward declarations,
// defines en includes. main() is niet meer hardcoded — de semantic analysis
// checkt of main aanwezig is.
//
// globalItem = alles wat op top-level mag staan:
//   - preprocessor directives (#include, #define)
//   - enum definities
//   - functie forward declarations:  int foo(int x);
//   - functie definities:            int foo(int x) { ... }
//   - globale variabele declaraties: int x = 5;
//   - comments
//
// EDGE CASE: volgorde maakt niet uit voor de parser, maar semantic analysis
//   checkt dat functies gedeclareerd zijn vóór gebruik.
program
    : globalItem* EOF
    ;

globalItem
    : includeStmt       // #include "file.h" of <stdio.h>
    | defineStmt        // #define oud nieuw
    | enumDef           // enum Status { ... };
    | funcDef           // int foo(int x) { ... }
    | funcDecl          // int foo(int x);   ← forward declaration
    | varDec            // globale variabele: int x = 5;
    | comment
    ;

// ── NIEUW: #include voor bestanden met aanhalingstekens ─────────────────────
// Voorbeeld: #include "some/folder/file.h"
// De preprocessor lost dit op VÓÓR de parser het ziet.
includeStmt
    : INCLUDE_STDIO         // #include <stdio.h>
    | INCLUDE_FILE          // #include "pad/naar/file.h"
    ;

// ── NIEUW: #define statement ─────────────────────────────────────────────────
// Voorbeeld: #define bool int
//            #define true 1
// De preprocessor vervangt alle voorkomens van OLD_VAL met NEW_VAL.
// EDGE CASE: slechts één define per lijn (zie opdracht).
defineStmt
    : DEFINE_STMT
    ;

// ── NIEUW: Enum definitie ────────────────────────────────────────────────────
// Syntax: enum <naam> { LABEL1, LABEL2, ... };
//
// Regels:
//   - Minimaal één label verplicht
//   - Trailing comma is NIET toegestaan (strikte C-stijl)
//   - Afgesloten met puntkomma
//
// EDGE CASE: lege enum body enum Foo {}; → parse error (minimaal 1 label)
// EDGE CASE: enum Foo { A, B, C, }; → parse error (geen trailing comma)
enumDef
    : ENUM_KW ID LBRACE ID (COMMA ID)* RBRACE SC
    ;

// ── NIEUW: Functie definitie ─────────────────────────────────────────────────
// Voorbeeld: int foo(int x, int y) { return x + y; }
//            void printHello() { ... }
//
// returnType is apart van 'type' omdat void alleen als returntype mag,
// niet als variabeletype.
//
// EDGE CASE: functie zonder parameters → paramList is leeg
// EDGE CASE: void return type
// EDGE CASE: pointer return type: int* foo() { ... }
funcDef
    : returnType ID LPAREN paramList RPAREN block
    ;

// ── NIEUW: Forward declaration ───────────────────────────────────────────────
// Voorbeeld: int foo(int x, int y);
//
// Semantic analysis checkt dat de definitie later overeenkomt
// in return type, aantal en types van parameters.
//
// EDGE CASE: forward declaration in header file → via #include opgelost
funcDecl
    : returnType ID LPAREN paramList RPAREN SC
    ;

// ── NIEUW: Return type (uitgebreid met void) ─────────────────────────────────
// void mag ALLEEN als returntype, niet als variabeletype.
returnType
    : VOID_KW               // void foo() { ... }
    | type                  // int foo() { ... } / int* foo() { ... }
    ;

// ── NIEUW: Parameter lijst ───────────────────────────────────────────────────
// Voorbeelden:
//   ()                     → lege parameterlijst
//   (int x)                → één parameter
//   (int x, float y)       → meerdere parameters
//   (const int* ptr)       → const pointer parameter
//
// EDGE CASE: lege parameterlijst is geldig (geen parameters)
paramList
    : (param (COMMA param)*)?
    ;

// ── NIEUW: Één parameter ─────────────────────────────────────────────────────
// Voorbeeld: int x / const float* ptr / char c
//
// EDGE CASE: parameter zonder naam is NIET ondersteund (bv. int foo(int, int))
//   → we vereisen altijd een naam
param
    : type ID
    ;

// ── UITGEBREID: alle nieuwe statement-soorten toegevoegd ────────────────────
// Volgorde is belangrijk voor ANTLR's disambiguatie:
//   - ifStmt / whileStmt / forStmt / switchStmt beginnen met een keyword → geen conflict
//   - scopeStmt begint met '{' → kan niet verward worden met andere regels
//   - varDec en arrayDec beginnen beide met 'type' → ANTLR kijkt verder (lookahead)
statement
    : varDec
    | arrayDec
    | varAss
    | functionCall SC
    | expression SC
    | comment
    | ifStmt          // ── NIEUW: if / if-else / else-if
    | whileStmt       // ── NIEUW: while lus
    | forStmt         // ── NIEUW: for lus
    | breakStmt       // ── NIEUW: break
    | continueStmt    // ── NIEUW: continue
    | switchStmt      // ── NIEUW: switch-case
    | scopeStmt       // ── NIEUW: anonieme scope { ... }
    | returnStmt      // ── NIEUW: return statement
    ;

// Een blok is een reeks statements tussen accolades: { ... }
// Ongewijzigd van assignment 3.
block
    : LBRACE (statement)* RBRACE
    ;

// ── NIEUW: If statement ──────────────────────────────────────────────────────
// Syntaxis: if (conditie) { ... }
//           if (conditie) { ... } else { ... }
//           if (conditie) { ... } else if (conditie) { ... }
//
// Curly braces zijn VERPLICHT (zie opdracht 4).
//
// Hoe werkt 'else if'?
//   We modelleren het als: else (block | ifStmt)
//   Dat betekent:
//     - else { ... }       → else + block  (normaal else)
//     - else if (...) { }  → else + ifStmt (recursief, geneste if)
//   Dit is eenvoudiger dan een aparte 'elseIfClause' regel en geeft
//   dezelfde parse boom.
//
// EDGE CASE: alleen if, geen else → de (ELSE_KW ...)? is optioneel
// EDGE CASE: geneste if/else: if(a) { if(b) {} else {} }
//   → door verplichte curly braces is er GEEN dangling-else probleem!
ifStmt
    : IF_KW LPAREN expression RPAREN block
      (ELSE_KW (block | ifStmt))?
    ;

// ── NIEUW: While statement ───────────────────────────────────────────────────
// Syntaxis: while (conditie) { ... }
//
// EDGE CASE: lege body: while (x > 0) {} → geldig
// EDGE CASE: altijd-true: while (1) { ... } → syntactisch geldig
whileStmt
    : WHILE_KW LPAREN expression RPAREN block
    ;

// ── NIEUW: For statement ─────────────────────────────────────────────────────
// Syntaxis: for (init; conditie; update) { ... }
//
// Alle drie de delen zijn optioneel:
//   for (;;) {}          → oneindige lus
//   for (int i=0;;)      → geen conditie, geen update
//   for (;i<10;i++)      → geen init
//
// BELANGRIJK: de init staat NIET in een gewone varDec/varAss,
// want die hebben al een ';' ingebakken. We gebruiken een aparte
// 'forInit' regel die GEEN ';' bevat.
//
// EDGE CASE: for met declaratie in init: for(int i=0; i<n; i++)
//   → forInit matcht: type ID (ASSIGN expression)?
// EDGE CASE: for met expressie in init:  for(i=0; i<n; i++)
//   → forInit matcht: expression  (i=0 wordt als expression geparseerd,
//     want varAss heeft ';' maar expression niet)
//
// LET OP: de update (derde deel) is een expressie, geen statement.
// Dus i++ is een geldige update (postfix ++ is een expressie).
forStmt
    : FOR_KW LPAREN forInit? SC expression? SC expression? RPAREN block
    ;

// Aparte regel voor de for-init (geen puntkomma aan het einde!)
//
// Twee alternatieven:
//   1. Declaratie: int i = 0     (type + naam + optionele waarde)
//   2. Expressie:  i = 0         (alle andere gevallen)
//
// EDGE CASE: voor het onderscheid tussen de twee alternatieven kijkt ANTLR
// naar het eerste token:
//   - Als het een type-keyword is (int/float/char/enum) → kies alternatief 1
//   - Anders → kies alternatief 2
forInit
    : type ID (ASSIGN expression)?   // int i = 0   (declaratie)
    | expression                      // i = 0, i++  (expressie)
    ;

// ── NIEUW: Break statement ───────────────────────────────────────────────────
// Geldig binnen: while-lus, for-lus, switch-statement.
// Semantic error als break buiten een loop/switch staat.
breakStmt
    : BREAK_KW SC
    ;

// ── NIEUW: Continue statement ────────────────────────────────────────────────
// Geldig binnen: while-lus, for-lus.
// Semantic error als continue buiten een lus staat.
//
// EDGE CASE: continue in for-lus → springt naar de UPDATE stap, niet naar conditie!
//   Dit wordt opgelost in de AST-constructie (for → while vertaling).
continueStmt
    : CONTINUE_KW SC
    ;

// ── NIEUW: Switch statement ──────────────────────────────────────────────────
// Syntaxis:
//   switch (x) {
//     case 1: statement* break;
//     case 2: statement* break;
//     default: statement*
//   }
//
// BELANGRIJK: switch heeft GEEN eigen scope in C!
// Variabele declaraties direct in switch body (niet in een anonieme scope)
// zijn een semantic error. Dit wordt gecheckt in de semantic analysis.
//
// EDGE CASE: geen default → defaultClause is optioneel
// EDGE CASE: meerdere case-labels op één body → niet ondersteund in onze grammar.
//   Elk case-label heeft zijn eigen statement-lijst.
// EDGE CASE: fallthrough (geen break aan het einde van een case) → syntactisch geldig,
//   maar we vertalen switch naar if-chain in de AST, dus fallthrough verdwijnt.
//   (Voor nu: we nemen aan dat elke case een break heeft of de laatste case is.)
switchStmt
    : SWITCH_KW LPAREN expression RPAREN LBRACE caseClause* defaultClause? RBRACE
    ;

// Een case-clause: case <expressie>: <statements>
// EDGE CASE: lege case body (geen statements) is syntactisch geldig
caseClause
    : CASE_KW expression COLON statement*
    ;

// De default-clause: default: <statements>
// EDGE CASE: lege default body is syntactisch geldig
defaultClause
    : DEFAULT_KW COLON statement*
    ;

// ── NIEUW: Anonieme scope ────────────────────────────────────────────────────
// Voorbeeld: { int x = 5; printf("%d", x); }
// Dit is gewoon een blok dat als statement optreedt.
//
// EDGE CASE: anonieme scope BINNEN een switch-body → hiermee kun je
//   variabelen declareren in een switch: case 1: { int x = 5; } break;
scopeStmt
    : block
    ;

// ── NIEUW: Return statement ──────────────────────────────────────────────────
// Voorbeelden:
//   return x + y;    → return met waarde
//   return;          → return zonder waarde (voor void functies)
//
// EDGE CASE: return met waarde in void functie → semantic error
// EDGE CASE: return met verkeerd type → semantic error
// EDGE CASE: return buiten een functie → semantic error
// EDGE CASE: code NA return in hetzelfde blok → dead code (optimalisatie)
returnStmt
    : RETURN_KW expression? SC
    ;

// ── UITGEBREID: Type ondersteunt nu ook enum types ──────────────────────────
// Voorbeeld: enum Status x = READY;
//
// EDGE CASE: enum type heeft geen pointer depth (geen 'enum Foo*' ondersteuning nodig).
// EDGE CASE: CONST_KW voor enum is niet ondersteund in onze subset.
//
// WAAROM enum_type als apart alternatief en niet in baseType?
//   enum_type heeft twee tokens (ENUM_KW + ID), terwijl baseType altijd
//   één token is. Door het apart te houden blijft baseType simpel.
type
    : CONST_KW? baseType CONST_KW? STAR*   // int, float, char (met optionele const en pointers)
    | ENUM_KW ID                 // enum Status  (geen const/pointer voor enums)
    ;

// De drie basistypen (ongewijzigd)
baseType
    : INT_KW
    | FLOAT_KW
    | CHAR_KW
    ;

// Variabele declaratie (ongewijzigd van assignment 3)
// Werkt ook voor enum variabelen: de 'type' regel vangt dat al op.
varDec
    : type ID (ASSIGN expression)? SC
    ;

// Array declaratie (ongewijzigd van assignment 3)
arrayDec
    : type ID (LBRACKET INTEGER RBRACKET)+ (ASSIGN arrayInit)? SC
    ;

// Array initialisator (ongewijzigd van assignment 3)
arrayInit
    : LBRACE (arrayElement (COMMA arrayElement)*)? RBRACE
    ;

arrayElement
    : expression
    | arrayInit
    ;

// Assignment statement (ongewijzigd van assignment 3)
varAss
    : expression ASSIGN expression SC
    ;

// Functie aanroep (ongewijzigd van assignment 3)
functionCall
    : ID LPAREN (expression (COMMA expression)*)? RPAREN
    ;

// Comment (ongewijzigd van assignment 3)
comment
    : LINE_COMMENT_TOKEN
    | BLOCK_COMMENT_TOKEN
    ;

// Expressies (ongewijzigd van assignment 3)
// Prioriteit: hogere regels = hogere prioriteit
expression
    : expression LBRACKET expression RBRACKET  // array toegang:    arr[i]
    | expression PLUSPLUS                       // suffix ++:        x++
    | expression MINUSMINUS                     // suffix --:        x--
    | functionCall                              // functie aanroep:  printf(...)
    | MINUS      expression                     // unaire min        (hogere prio dan binaire *)
    | PLUS       expression                     // unaire plus
    | EXMARK     expression                     // logische NOT
    | TILDE      expression                     // bitwise NOT
    | AND        expression                     // address-of: &x
    | STAR       expression                     // pointer deref: *ptr
    | PLUSPLUS   expression                     // prefix ++
    | MINUSMINUS expression                     // prefix --
    | LPAREN type RPAREN expression             // cast: (int) x
    | expression STAR        expression         // vermenigvuldiging
    | expression SLASH       expression         // deling
    | expression PERCENT     expression         // modulo
    | expression PLUS        expression         // optelling
    | expression MINUS       expression         // aftrekking
    | expression LSHIFT      expression         // shift left
    | expression RSHIFT      expression         // shift right
    | expression LT          expression         // kleiner dan
    | expression LEQ         expression         // kleiner of gelijk
    | expression GT          expression         // groter dan
    | expression GEQ         expression         // groter of gelijk
    | expression EQ          expression         // gelijk aan
    | expression NOTEQ       expression         // niet gelijk aan
    | expression AND         expression         // bitwise AND
    | expression HAT         expression         // bitwise XOR
    | expression OR          expression         // bitwise OR
    | expression ANDAND      expression         // logische AND
    | expression OROR        expression         // logische OR
    | LPAREN expression RPAREN                  // haakjes: (3 + 4)
    | INTEGER                                   // integer literal: 42
    | FLOAT                                     // float literal: 3.14
    | ID                                        // variabele of enum label: x, READY
    | CHAR                                      // char literal: 'a'
    | STRING                                    // string literal: "hello"
    ;

// --------------------
// Lexer rules
// --------------------
// VOLGORDE IS KRITISCH:
//   1. Langere / meerdere-karakter tokens VOOR kortere
//   2. Keywords VOOR ID (anders wordt 'if' als ID herkend!)

// Whitespace: overslaan
WS : [ \n\t\r]+ -> skip ;

// Comments (als gewone tokens — zie assignment 3 voor uitleg)
LINE_COMMENT_TOKEN  : '//' ~[\r\n]* ;
BLOCK_COMMENT_TOKEN : '/*' (~'*' | '*'+ ~[*/])* '*'+ '/' ;

// #include <stdio.h> als één token (ongewijzigd)
INCLUDE_STDIO : '#' [ \t]* 'include' [ \t]* '<stdio.h>' ;

// ── NIEUW: Preprocessor tokens ───────────────────────────────────────────────
// Deze worden door de preprocessor afgehandeld VÓÓR de parser,
// maar we definiëren ze als tokens zodat de grammar ze kan herkennen.
//
// #include "pad/naar/file.h"
INCLUDE_FILE : '#' [ \t]* 'include' [ \t]* '"' ~["\r\n]+ '"' ;

// #define oud nieuw  (alles op één lijn na #define)
DEFINE_STMT  : '#' [ \t]* 'define' [ \t]+ ~[\r\n]+ ;

// ── NIEUW: Keywords voor functies ────────────────────────────────────────────
VOID_KW   : 'void'   ;
RETURN_KW : 'return' ;

// ── NIEUW: Keywords voor control flow en enums ───────────────────────────────
// VERPLICHT vóór de ID regel, anders worden ze als identifier herkend!
IF_KW       : 'if'       ;
ELSE_KW     : 'else'     ;
WHILE_KW    : 'while'    ;
FOR_KW      : 'for'      ;
BREAK_KW    : 'break'    ;
CONTINUE_KW : 'continue' ;
SWITCH_KW   : 'switch'   ;
CASE_KW     : 'case'     ;
DEFAULT_KW  : 'default'  ;
ENUM_KW     : 'enum'     ;

// Bestaande type-keywords (ongewijzigd)
INT_KW   : 'int'   ;
CONST_KW : 'const' ;
CHAR_KW  : 'char'  ;
FLOAT_KW : 'float' ;

// Literals
fragment DIGIT : [0-9] ;
INTEGER : DIGIT+ ;
FLOAT   : DIGIT+ '.' DIGIT+ ;

CHAR   : '\'' ( '\\' [btnfr0'\\] | ~['\\\r\n] ) '\'' ;
STRING : '"' ( '\\' [ntr"\\] | ~["\\\r\n] )* '"' ;

// Identifier (NA keywords, zodat 'if' niet als ID herkend wordt)
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
LBRACKET : '[' ;
RBRACKET : ']' ;
COMMA    : ',' ;
COLON    : ':' ;   // ── NIEUW: voor switch case / default