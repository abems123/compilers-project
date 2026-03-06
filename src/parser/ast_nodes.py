# src/parser/ast_nodes.py
#
# Bevat alle AST node klassen voor de compiler.
# Assignment 3 voegde toe:
#   - CommentNode        (comments bewaren in AST)
#   - ArrayDeclNode      (array declaraties)
#   - ArrayAccessNode    (array toegang: arr[i], arr[i][j])
#   - ArrayInitNode      (array initialisatoren: {1, 2, 3})
#   - StringLiteralNode  (string literals: "hello")
#   - FunctionCallNode   (printf, scanf, enz.)
#   - IncludeNode        (#include <stdio.h>)
#
# Assignment 4 voegt toe:
#   - EnumDefNode        (enum definitie: enum Status { READY, BUSY };)
#   - IfNode             (if / if-else / else-if)
#   - WhileNode          (while-lus, ook gebruikt voor vertaalde for-lussen)
#   - BreakNode          (break statement)
#   - ContinueNode       (continue statement)
#   - ScopeNode          (anonieme scope { ... })
#
# ProgramNode is uitgebreid met een 'enums' lijst (naast de bestaande 'includes').


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
# STRUCTUUR NODES
# ============================================================

class ProgramNode(ASTNode):
    """
    De root van de hele AST. Stelt het volledige C bestand voor.

    Assignment 3 uitbreiding: 'includes' lijst voor stdio.h check.
    Assignment 4 uitbreiding: 'enums' lijst voor globale enum definities.

    WAAROM enums apart bijhouden?
      De semantic analysis moet enum labels kennen VOORDAT ze de body
      van main() bezoekt. Als we enums apart opslaan in ProgramNode,
      kan de semantic analysis ze in één eerste pass verwerken en
      daarna pas de body analyseren.

    EDGE CASE: de volgorde van enums in de lijst komt overeen met de
    volgorde in de broncode. Dit is belangrijk als een enum label
    gebruikt wordt in een volgende enum definitie (niet ondersteund
    in onze subset, maar de volgorde klopt wel).

    EDGE CASE: backwards-compatibiliteit — bestaande code die
    ProgramNode(body) of ProgramNode(body, includes) aanroept
    blijft werken dankzij de default waarden.
    """
    def __init__(self, body: 'BlockNode', includes: list = None, enums: list = None):
        self.body     = body
        self.includes = includes if includes is not None else []
        # lijst van EnumDefNode objecten — leeg als er geen enums zijn
        self.enums    = enums    if enums    is not None else []

    def accept(self, visitor):
        return visitor.visitProgram(self)

    def __repr__(self):
        return f"ProgramNode(includes={self.includes}, enums={self.enums}, {self.body})"


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
    Beschrijft een type zoals: int, const float*, char**, enum Status.
    Ongewijzigd van assignment 2 — de 'enum Status' case wordt
    gerepresenteerd als TypeNode('Status', 0, False) met base_type = 'Status'.
    De semantic analysis herkent enum types via de symbol table.
    """
    def __init__(self, base_type: str, pointer_depth: int = 0, is_const: bool = False):
        self.base_type     = base_type      # 'int', 'float', 'char', of enum naam
        self.pointer_depth = pointer_depth  # 0 = geen pointer, 1 = *, 2 = **
        self.is_const      = is_const

    def accept(self, visitor):
        return visitor.visitType(self)

    def __repr__(self):
        const_str = "const " if self.is_const else ""
        stars     = "*" * self.pointer_depth
        return f"TypeNode({const_str}{self.base_type}{stars})"


# ============================================================
# DECLARATIE EN ASSIGNMENT NODES (ongewijzigd)
# ============================================================

class VarDeclNode(ASTNode):
    """
    Variabele declaratie, met of zonder initialisatie.
    Ongewijzigd van assignment 2.

    Voorbeeld: int x = 5;  →  VarDeclNode(TypeNode('int'), 'x', LiteralNode(5))
    Voorbeeld: enum Status s = BUSY; → VarDeclNode(TypeNode('Status'), 's', VariableNode('BUSY'))
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
# ARRAY NODES (ongewijzigd van assignment 3)
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

    EDGE CASE: dimensions is altijd een lijst van ints (geen expressies).
    EDGE CASE: var_type bevat het basistype van de ELEMENTEN, niet van het array zelf.
    """
    def __init__(self, var_type: TypeNode, name: str,
                 dimensions: list, initializer: 'ArrayInitNode' = None):
        self.var_type    = var_type
        self.name        = name
        self.dimensions  = dimensions
        self.initializer = initializer

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

    EDGE CASE: lege initialisator {} → elements = []
    """
    def __init__(self, elements: list):
        self.elements = elements

    def accept(self, visitor):
        return visitor.visitArrayInit(self)

    def __repr__(self):
        return f"ArrayInitNode({self.elements})"


class ArrayAccessNode(ASTNode):
    """
    Array toegang: arr[i], arr[i][j].

    Voor multi-dimensionale toegang nestelen we ArrayAccessNodes:
      arr[i][j] → ArrayAccessNode(ArrayAccessNode(VariableNode('arr'), i), j)

    EDGE CASE: de index kan een willekeurige expressie zijn.
    """
    def __init__(self, array_expr: ASTNode, index: ASTNode):
        self.array_expr = array_expr
        self.index      = index

    def accept(self, visitor):
        return visitor.visitArrayAccess(self)

    def __repr__(self):
        return f"ArrayAccessNode({self.array_expr}, {self.index})"


# ============================================================
# EXPRESSIE NODES (ongewijzigd van assignment 3)
# ============================================================

class LiteralNode(ASTNode):
    """
    Een concrete waarde: integer, float of char.
    Ongewijzigd van assignment 2.
    """
    def __init__(self, value, type_name: str):
        self.value     = value
        self.type_name = type_name  # 'int', 'float', of 'char'

    def accept(self, visitor):
        return visitor.visitLiteral(self)

    def __repr__(self):
        return f"LiteralNode({self.value!r}, {self.type_name})"


class StringLiteralNode(ASTNode):
    """
    Een string literal: "hello", "Number: %d\n", enz.
    We slaan de RAW waarde op (tussen de aanhalingstekens, zonder de quotes).
    Ongewijzigd van assignment 3.
    """
    def __init__(self, value: str):
        self.value = value

    def accept(self, visitor):
        return visitor.visitStringLiteral(self)

    def __repr__(self):
        return f"StringLiteralNode({self.value!r})"


class VariableNode(ASTNode):
    """
    Een identifier in een expressie.
    Ongewijzigd van assignment 2.

    NIEUW in assignment 4: wordt ook gebruikt voor enum labels (READY, BUSY, enz.)
    De semantic analysis onderscheidt gewone variabelen van enum labels via de
    symbol table.
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
# I/O EN STRUCTUUR NODES (ongewijzigd van assignment 3)
# ============================================================

class FunctionCallNode(ASTNode):
    """
    Een functie aanroep zoals printf of scanf.
    Ongewijzigd van assignment 3.
    """
    def __init__(self, name: str, args: list):
        self.name = name
        self.args = args

    def accept(self, visitor):
        return visitor.visitFunctionCall(self)

    def __repr__(self):
        return f"FunctionCallNode({self.name!r}, {self.args})"


class CommentNode(ASTNode):
    """
    Een comment die bewaard wordt in de AST.
    Ongewijzigd van assignment 3.
    """
    def __init__(self, text: str):
        self.text = text

    def accept(self, visitor):
        return visitor.visitComment(self)

    def __repr__(self):
        preview = self.text[:40].replace('\n', '\\n')
        return f"CommentNode({preview!r})"


class IncludeNode(ASTNode):
    """
    Een #include statement.
    Ongewijzigd van assignment 3.
    """
    def __init__(self, header: str):
        self.header = header  # 'stdio.h'

    def accept(self, visitor):
        return visitor.visitInclude(self)

    def __repr__(self):
        return f"IncludeNode({self.header!r})"


# ============================================================
# ASSIGNMENT 4 — ENUM NODE
# ============================================================

class EnumDefNode(ASTNode):
    """
    Een enum definitie buiten main().

    Voorbeeld:
      enum SYS_IO_ReceiverStatusBit { READY, BUSY, OFFLINE };
      → EnumDefNode('SYS_IO_ReceiverStatusBit', ['READY', 'BUSY', 'OFFLINE'])

    DESIGN KEUZE: labels zijn een lijst van strings. De waarden zijn
    impliciet 0, 1, 2, ... (geen custom waarden per opdracht).

    EDGE CASE: labels worden door de semantic analysis als 'const int'
    variabelen in de GLOBALE scope geregistreerd met waarden 0, 1, 2, ...
    Zo werkt READY + 1 gewoon als een integer expressie.

    EDGE CASE: een enum label mag niet dezelfde naam hebben als een
    bestaande variabele in dezelfde scope. Semantic analysis checkt dit.

    EDGE CASE: enum labels zijn GLOBAAL zichtbaar — ook binnen geneste
    scopes, zonder scope qualifier (C-stijl unscoped enums).
    """
    def __init__(self, name: str, labels: list):
        self.name   = name    # 'SYS_IO_ReceiverStatusBit'
        self.labels = labels  # ['READY', 'BUSY', 'OFFLINE']

    def accept(self, visitor):
        return visitor.visitEnumDef(self)

    def __repr__(self):
        return f"EnumDefNode({self.name!r}, {self.labels})"


# ============================================================
# ASSIGNMENT 4 — CONTROL FLOW NODES
# ============================================================

class IfNode(ASTNode):
    """
    Een if-statement, met optionele else-tak.

    Voorbeelden:
      if (x > 0) { ... }
        → IfNode(condition, then_block, else_block=None)

      if (x > 0) { ... } else { ... }
        → IfNode(condition, then_block, else_block=BlockNode([...]))

      if (x > 0) { ... } else if (x == 0) { ... } else { ... }
        → IfNode(condition, then_block,
              else_block=IfNode(condition2, then_block2,
                  else_block=BlockNode([...])))

    EDGE CASE: else_block kan None, BlockNode of IfNode zijn.
    EDGE CASE: lege then- of else-body: BlockNode([]) is geldig.
    EDGE CASE: geen dangling-else probleem door verplichte curly braces
               in de grammar.
    """
    def __init__(self, condition: ASTNode, then_block: BlockNode,
                 else_block: ASTNode = None):
        self.condition  = condition   # de test-expressie
        self.then_block = then_block  # de if-tak (BlockNode)
        self.else_block = else_block  # de else-tak (BlockNode, IfNode, of None)

    def accept(self, visitor):
        return visitor.visitIf(self)

    def __repr__(self):
        return (f"IfNode(cond={self.condition}, "
                f"then={self.then_block}, else={self.else_block})")


class WhileNode(ASTNode):
    """
    Een while-lus. Wordt ook gebruikt voor de for → while vertaling.

    Voorbeeld (while):
      while (x < 10) { x = x + 1; }
        → WhileNode(condition=BinaryOpNode('<', ...), body=BlockNode([...]))

    Voorbeeld (for → while vertaling):
      for (int i = 0; i < 10; i++) { ... }
      Wordt in de CST→AST visitor omgezet naar:
        VarDeclNode('i', 0)          ← init statement vóór de WhileNode
        WhileNode(
          condition = BinaryOpNode('<', VariableNode('i'), LiteralNode(10)),
          body      = BlockNode([..., AssignNode(i, i+1)]),  ← update in body
          update    = BinaryOpNode('+', VariableNode('i'), LiteralNode(1))
        )

    WAAROM 'update' apart opslaan?
      Bij een 'continue' in een for-lus moet de update-stap (i++) nog
      uitgevoerd worden vóór de volgende iteratie. De LLVM visitor kijkt
      naar WhileNode.update om te weten waar 'continue' naartoe springt:
        - update is None → continue springt direct naar de conditie (normale while)
        - update is niet None → continue springt naar het update-label (for-lus)

    EDGE CASE: lege conditie in for (for(;;)) → condition = LiteralNode(1, 'int')
    EDGE CASE: lege body: WhileNode(cond, BlockNode([])) is geldig.
    """
    def __init__(self, condition: ASTNode, body: BlockNode,
                 update: ASTNode = None):
        self.condition = condition   # de test-expressie
        self.body      = body        # het herhaalde blok
        self.update    = update      # optioneel: for-lus update expressie (i++)

    def accept(self, visitor):
        return visitor.visitWhile(self)

    def __repr__(self):
        return (f"WhileNode(cond={self.condition}, "
                f"body={self.body}, update={self.update})")


class BreakNode(ASTNode):
    """
    Een break statement.

    Springt uit de dichtstbijzijnde lus of switch.

    EDGE CASE: break buiten een lus/switch → semantic error.
               De semantic analysis checkt dit via een 'loop_depth' teller.
    EDGE CASE: break in een switch die in een lus zit → springt alleen
               uit de switch, niet uit de lus. De LLVM visitor regelt dit
               via een stack van exit-labels.
    """
    def accept(self, visitor):
        return visitor.visitBreak(self)

    def __repr__(self):
        return "BreakNode()"


class ContinueNode(ASTNode):
    """
    Een continue statement.

    Springt naar de volgende iteratie van de dichtstbijzijnde lus.

    EDGE CASE: continue buiten een lus → semantic error.
    EDGE CASE: continue in een for-lus (vertaald naar while) →
               springt naar het update-label, niet direct naar de conditie.
               De LLVM visitor herkent dit via WhileNode.update.
    """
    def accept(self, visitor):
        return visitor.visitContinue(self)

    def __repr__(self):
        return "ContinueNode()"


# ============================================================
# ASSIGNMENT 4 — SCOPE NODE
# ============================================================

class ScopeNode(ASTNode):
    """
    Een anonieme scope: een blok tussen accolades dat als statement optreedt.

    Voorbeeld:
      { int x = 5; printf("%d", x); }
        → ScopeNode(body=BlockNode([VarDeclNode(...), FunctionCallNode(...)]))

    WAAROM ScopeNode en niet gewoon BlockNode als statement?
      BlockNode wordt al gebruikt als de body van if/while/for.
      ScopeNode maakt het expliciet dat dit een ANONIEME scope is als
      zelfstandig statement. Hierdoor kan de DOT visualisatie en de
      semantic analysis het onderscheid maken.

    EDGE CASE: anonieme scope in een switch body maakt variabele declaratie
               in switch WEL mogelijk:
                 switch(x) { case 1: { int y = 0; } break; }
    EDGE CASE: geneste anonieme scopes: { { int x = 1; } int x = 2; }
               De binnenste x is alleen zichtbaar in de binnenste scope.
               Dit werkt automatisch via push_scope()/pop_scope() in de
               semantic analysis en LLVM visitor.
    """
    def __init__(self, body: BlockNode):
        self.body = body

    def accept(self, visitor):
        return visitor.visitScope(self)

    def __repr__(self):
        return f"ScopeNode({self.body})"