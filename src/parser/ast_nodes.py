# src/parser/ast_nodes.py
#
# Bevat alle AST node klassen voor de compiler.
# Assignment 3 voegt toe:
#   - CommentNode        (comments bewaren in AST)
#   - ArrayDeclNode      (array declaraties)
#   - ArrayAccessNode    (array toegang: arr[i], arr[i][j])
#   - ArrayInitNode      (array initialisatoren: {1, 2, 3})
#   - StringLiteralNode  (string literals: "hello")
#   - FunctionCallNode   (printf, scanf, enz.)
#   - IncludeNode        (#include <stdio.h>)
#
# ProgramNode is uitgebreid met een 'includes' lijst.


# ============================================================
# BASIS KLASSE
# ============================================================

class ASTNode:
    """
    Basisklasse voor alle AST nodes.
    Elke subklasse moet accept() implementeren voor het visitor pattern.
    """
    def accept(self, visitor):
        raise NotImplementedError("Elke subklasse moet accept() implementeren")


# ============================================================
# STRUCTUUR NODES (ongewijzigd + uitbreiding ProgramNode)
# ============================================================

class ProgramNode(ASTNode):
    """
    De root van de hele AST. Stelt het volledige C bestand voor.

    Assignment 3 uitbreiding: includes bijhouden zodat de semantic
    analysis kan checken of stdio.h aanwezig is voor printf/scanf.

    Voorbeeld voor:
        #include <stdio.h>
        int main() { ... }

    → ProgramNode(
          includes=[IncludeNode('stdio.h')],
          body=BlockNode([...])
      )

    EDGE CASE: includes is een lijst (niet één waarde) zodat we
    meerdere includes aankunnen. In practice verwachten we er maximaal
    één, maar de grammar staat er meerdere toe.
    """
    def __init__(self, body: 'BlockNode', includes: list = None):
        # de body is de BlockNode van de main functie
        self.body = body

        # lijst van IncludeNode objecten — leeg als er geen includes zijn
        # We gebruiken None als default en zetten het om naar [] zodat
        # bestaande code die ProgramNode(body) aanroept nog werkt.
        self.includes = includes if includes is not None else []

    def accept(self, visitor):
        return visitor.visitProgram(self)

    def __repr__(self):
        return f"ProgramNode(includes={self.includes}, {self.body})"


class BlockNode(ASTNode):
    """
    Een blok van statements tussen accolades { ... }.
    Bevat een lijst van ASTNodes (de statements).
    Ongewijzigd van assignment 2.
    """
    def __init__(self, statements: list):
        self.statements = statements

    def accept(self, visitor):
        return visitor.visitBlock(self)

    def __repr__(self):
        return f"BlockNode({self.statements})"


# ============================================================
# TYPE NODE (ongewijzigd)
# ============================================================

class TypeNode(ASTNode):
    """
    Beschrijft een type zoals: int, const float*, char**.
    Ongewijzigd van assignment 2.
    """
    def __init__(self, base_type: str, pointer_depth: int = 0, is_const: bool = False):
        self.base_type     = base_type      # 'int', 'float', 'char'
        self.pointer_depth = pointer_depth  # 0 = geen pointer, 1 = *, 2 = **
        self.is_const      = is_const

    def accept(self, visitor):
        return visitor.visitType(self)

    def __repr__(self):
        const_str = "const " if self.is_const else ""
        stars     = "*" * self.pointer_depth
        return f"TypeNode({const_str}{self.base_type}{stars})"


# ============================================================
# DECLARATIE EN ASSIGNMENT NODES
# ============================================================

class VarDeclNode(ASTNode):
    """
    Variabele declaratie, met of zonder initialisatie.
    Ongewijzigd van assignment 2.

    Voorbeeld: int x = 5;  →  VarDeclNode(TypeNode('int'), 'x', LiteralNode(5))
    """
    def __init__(self, var_type: TypeNode, name: str, value: ASTNode = None):
        self.var_type = var_type
        self.name     = name
        self.value    = value  # None als er geen initialisatie is

    def accept(self, visitor):
        return visitor.visitVarDecl(self)

    def __repr__(self):
        return f"VarDeclNode({self.var_type}, {self.name!r}, value={self.value})"


class AssignNode(ASTNode):
    """
    Assignment statement: target = value.
    De linkerkant is een expressie (lvalue): VariableNode of UnaryOpNode('*', ...).
    Ongewijzigd van assignment 2.
    """
    def __init__(self, target: ASTNode, value: ASTNode):
        self.target = target
        self.value  = value

    def accept(self, visitor):
        return visitor.visitAssign(self)

    def __repr__(self):
        return f"AssignNode({self.target}, {self.value})"


# ============================================================
# ARRAY NODES (NIEUW in assignment 3)
# ============================================================

class ArrayDeclNode(ASTNode):
    """
    Array declaratie, met of zonder initialisatie.

    Voorbeelden:
      int arr[3];
        → ArrayDeclNode(TypeNode('int'), 'arr', [3], None)

      int arr[3] = {1, 2, 3};
        → ArrayDeclNode(TypeNode('int'), 'arr', [3], ArrayInitNode([...]))

      int matrix[2][4];
        → ArrayDeclNode(TypeNode('int'), 'matrix', [2, 4], None)

      float grid[2][3] = {{1.0, 2.0, 3.0}, {4.0, 5.0, 6.0}};
        → ArrayDeclNode(TypeNode('float'), 'grid', [2, 3],
              ArrayInitNode([ArrayInitNode([...]), ArrayInitNode([...])]))

    EDGE CASE: dimensions is altijd een lijst van ints (geen expressies).
    De grammar dwingt dit af door alleen INTEGER tokens toe te staan als dimensie.

    EDGE CASE: var_type bevat het basistype van de ELEMENTEN, niet van het array zelf.
    Een 'int arr[3]' heeft var_type = TypeNode('int'), niet TypeNode('int[]').
    """
    def __init__(self, var_type: TypeNode, name: str,
                 dimensions: list, initializer: 'ArrayInitNode' = None):
        self.var_type    = var_type      # type van de elementen: int, float, char
        self.name        = name          # naam van de array variabele
        self.dimensions  = dimensions    # lijst van ints: [3] of [2, 4] enz.
        self.initializer = initializer   # ArrayInitNode of None

    def accept(self, visitor):
        return visitor.visitArrayDecl(self)

    def __repr__(self):
        dims = ''.join(f'[{d}]' for d in self.dimensions)
        return f"ArrayDeclNode({self.var_type}, {self.name!r}{dims}, init={self.initializer})"


class ArrayInitNode(ASTNode):
    """
    Array initialisator: { ... }

    De elementen kunnen twee dingen zijn:
      - een gewone expressie (voor 1D arrays):    {1, x+2, -9}
      - een geneste ArrayInitNode (voor 2D+):     {{1,2}, {3,4}}

    EDGE CASE: lege initialisator {} is toegestaan door de grammar.
    De semantic analysis zal controleren of de lengte klopt met de dimensie.

    EDGE CASE: geneste diepte kan variëren — een 3D array heeft drie niveaus
    van ArrayInitNode nesting. Dit werkt automatisch doordat elementen
    ASTNode zijn en dus ook ArrayInitNode kunnen zijn.

    Voorbeelden:
      {1, 2, 3}         → ArrayInitNode([LiteralNode(1), LiteralNode(2), LiteralNode(3)])
      {{1,2}, {3,4}}    → ArrayInitNode([ArrayInitNode([...]), ArrayInitNode([...])])
      {}                → ArrayInitNode([])
    """
    def __init__(self, elements: list):
        # lijst van ASTNode — elk element is een expressie of een ArrayInitNode
        self.elements = elements

    def accept(self, visitor):
        return visitor.visitArrayInit(self)

    def __repr__(self):
        return f"ArrayInitNode({self.elements})"


class ArrayAccessNode(ASTNode):
    """
    Array toegang: het indexeren van een array element.

    Voorbeelden:
      arr[i]      → ArrayAccessNode(VariableNode('arr'), VariableNode('i'))
      arr[2]      → ArrayAccessNode(VariableNode('arr'), LiteralNode(2))
      matrix[i][j]
        → ArrayAccessNode(
              ArrayAccessNode(VariableNode('matrix'), VariableNode('i')),
              VariableNode('j')
          )

    EDGE CASE: voor multi-dimensionale toegang (arr[i][j]) nestelen we
    ArrayAccessNodes. De CST visitor bouwt dit automatisch doordat
    'expression[expression]' links-recursief is in de grammar.
    arr[i][j] wordt geparseerd als (arr[i])[j]:
      - eerste stap: ArrayAccessNode(VariableNode('arr'), i)
      - tweede stap: ArrayAccessNode(dat resultaat, j)

    EDGE CASE: de index kan een willekeurige expressie zijn, niet alleen
    een variabele of literal. De semantic analysis controleert dat het
    type van de index een int is.

    DESIGN KEUZE: we slaan de array_expr op als ASTNode (niet als string),
    zodat we ook expressies als base kunnen hebben, bijvoorbeeld:
      getArray()[0]  (als we ooit functies met return waarden ondersteunen)
    """
    def __init__(self, array_expr: ASTNode, index: ASTNode):
        # het ding dat geïndexeerd wordt: VariableNode of ArrayAccessNode (voor nesting)
        self.array_expr = array_expr

        # de index expressie: moet van type int zijn (check in semantic analysis)
        self.index = index

    def accept(self, visitor):
        return visitor.visitArrayAccess(self)

    def __repr__(self):
        return f"ArrayAccessNode({self.array_expr}, {self.index})"


# ============================================================
# EXPRESSIE NODES
# ============================================================

class LiteralNode(ASTNode):
    """
    Een concrete waarde: integer, float of char.
    Ongewijzigd van assignment 2.
    """
    def __init__(self, value, type_name: str):
        self.value     = value      # de Python waarde: int, float, of str
        self.type_name = type_name  # 'int', 'float', of 'char'

    def accept(self, visitor):
        return visitor.visitLiteral(self)

    def __repr__(self):
        return f"LiteralNode({self.value!r}, {self.type_name})"


class StringLiteralNode(ASTNode):
    """
    Een string literal: "hello", "Number: %d\n", enz.

    EDGE CASE: we slaan de RAW waarde op — de tekst TUSSEN de aanhalingstekens,
    maar ZONDER de aanhalingstekens zelf. Dus "hello\n" wordt opgeslagen als
    de string hello\n (met een echte backslash-n, nog niet verwerkt).

    Waarom niet direct verwerken?
    Omdat de LLVM codegen de escape sequences zelf moet omzetten naar
    LLVM's eigen formaat. Bijvoorbeeld: \n wordt \0A in LLVM strings.
    Als we hier al verwerken, verliezen we de originele representatie.

    EDGE CASE: lege string "" → StringLiteralNode("")

    EDGE CASE: string met %% → wordt door printf verwerkt als literal %,
    maar wij hoeven dat niet zelf te doen. We geven de raw string door.

    Voorbeeld:
      "hello\n"  → StringLiteralNode("hello\\n")
      ""         → StringLiteralNode("")
      "%d items" → StringLiteralNode("%d items")
    """
    def __init__(self, value: str):
        # de tekst van de string, zonder aanhalingstekens, met escape sequences intact
        self.value = value

    def accept(self, visitor):
        return visitor.visitStringLiteral(self)

    def __repr__(self):
        return f"StringLiteralNode({self.value!r})"


class VariableNode(ASTNode):
    """
    Een identifier in een expressie.
    Ongewijzigd van assignment 2.
    """
    def __init__(self, name: str):
        self.name = name

    def accept(self, visitor):
        return visitor.visitVariable(self)

    def __repr__(self):
        return f"VariableNode({self.name!r})"


class BinaryOpNode(ASTNode):
    """
    Een binaire operatie met twee operanden.
    Ongewijzigd van assignment 2.
    """
    def __init__(self, op: str, left: ASTNode, right: ASTNode):
        self.op    = op
        self.left  = left
        self.right = right

    def accept(self, visitor):
        return visitor.visitBinaryOp(self)

    def __repr__(self):
        return f"BinaryOpNode({self.op!r}, {self.left}, {self.right})"


class UnaryOpNode(ASTNode):
    """
    Een unaire operatie met één operand.
    Ongewijzigd van assignment 2.
    """
    def __init__(self, op: str, operand: ASTNode):
        self.op      = op
        self.operand = operand

    def accept(self, visitor):
        return visitor.visitUnaryOp(self)

    def __repr__(self):
        return f"UnaryOpNode({self.op!r}, {self.operand})"


class CastNode(ASTNode):
    """
    Een expliciete type cast: (int) x, (float*) ptr.
    Ongewijzigd van assignment 2.
    """
    def __init__(self, target_type: TypeNode, operand: ASTNode):
        self.target_type = target_type
        self.operand     = operand

    def accept(self, visitor):
        return visitor.visitCast(self)

    def __repr__(self):
        return f"CastNode({self.target_type}, {self.operand})"


# ============================================================
# FUNCTIE AANROEP (NIEUW in assignment 3)
# ============================================================

class FunctionCallNode(ASTNode):
    """
    Een functie aanroep zoals printf of scanf.

    Voorbeelden:
      printf("hello\n")
        → FunctionCallNode('printf', [StringLiteralNode("hello\\n")])

      printf("x = %d\n", x)
        → FunctionCallNode('printf', [StringLiteralNode("x = %d\\n"),
                                      VariableNode('x')])

      scanf("%d", &x)
        → FunctionCallNode('scanf', [StringLiteralNode("%d"),
                                     UnaryOpNode('&', VariableNode('x'))])

      printf("hello")   (geen extra args)
        → FunctionCallNode('printf', [StringLiteralNode("hello")])

    EDGE CASE: args kan leeg zijn. De grammar staat dit toe via de optionele
    argumentenlijst. Een aanroep als printf() zonder argumenten is syntactisch
    geldig (de semantic analysis zal later klagen als het nodig is).

    EDGE CASE: de naam is gewoon een string. We maken hier geen onderscheid
    tussen 'printf', 'scanf', of een andere functienaam. De semantic analysis
    checkt of de naam geldig is en of stdio.h geïncludeerd is.

    DESIGN KEUZE: name is een str (niet een VariableNode), omdat een
    functienaam geen variabele is — je kan geen functiepointer via een
    variabele aanroepen in onze subset van C.
    """
    def __init__(self, name: str, args: list):
        self.name = name    # naam van de functie: 'printf', 'scanf', enz.
        self.args = args    # lijst van ASTNode argumenten (kan leeg zijn)

    def accept(self, visitor):
        return visitor.visitFunctionCall(self)

    def __repr__(self):
        return f"FunctionCallNode({self.name!r}, {self.args})"


# ============================================================
# COMMENT NODE (NIEUW in assignment 3)
# ============================================================

class CommentNode(ASTNode):
    """
    Een comment die bewaard wordt in de AST.

    In assignment 3 worden comments NIET meer geskipped, maar opgeslagen
    zodat ze later in de LLVM output kunnen verschijnen als ';' commentaar.

    Voorbeelden:
      // dit is een comment
        → CommentNode("// dit is een comment")

      /* dit is een
         multi-line comment */
        → CommentNode("/* dit is een\n   multi-line comment */")

    EDGE CASE: we slaan de VOLLEDIGE token tekst op, inclusief de
    // of /* */ delimiters. Dit maakt het makkelijk om later in de
    LLVM output te zetten: vervang gewoon '//' door ';' en verwijder '/*' en '*/'.

    EDGE CASE: een lege comment // geeft CommentNode("//").
    Een lege block comment /**/ geeft CommentNode("/**/").

    EDGE CASE: de LLVM output mag alleen ';' comments op één regel hebben.
    De LLVM visitor moet multi-line block comments dus splitsen op newlines
    en elke regel prefixen met ';'.
    """
    def __init__(self, text: str):
        # de volledige commenttekst inclusief // of /* */ delimiters
        self.text = text

    def accept(self, visitor):
        return visitor.visitComment(self)

    def __repr__(self):
        # trim voor leesbaarheid in debug output
        preview = self.text[:40].replace('\n', '\\n')
        return f"CommentNode({preview!r})"


# ============================================================
# INCLUDE NODE (NIEUW in assignment 3)
# ============================================================

class IncludeNode(ASTNode):
    """
    Een #include statement bovenaan het programma.

    Momenteel ondersteunen we alleen #include <stdio.h>.
    De semantic analysis gebruikt de aanwezigheid van IncludeNode('stdio.h')
    om te bepalen of printf en scanf gebruikt mogen worden.

    EDGE CASE: meerdere includes zijn syntactisch toegestaan door de grammar
    (includeStmt*). De semantic analysis hoeft alleen te checken of
    'stdio.h' ergens in de includes lijst staat.

    EDGE CASE: we slaan alleen de headernaam op ('stdio.h'), niet de
    volledige include-tekst. Zo kunnen we makkelijk vergelijken in
    de semantic analysis: if any(inc.header == 'stdio.h' for inc in includes).

    Voorbeeld:
      #include <stdio.h>  →  IncludeNode('stdio.h')
    """
    def __init__(self, header: str):
        # de naam van de header, zonder < > of aanhalingstekens
        self.header = header  # 'stdio.h'

    def accept(self, visitor):
        return visitor.visitInclude(self)

    def __repr__(self):
        return f"IncludeNode({self.header!r})"