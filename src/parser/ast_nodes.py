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

    Assignment 5 herbouw: in plaats van één vaste 'body' (BlockNode voor main)
    bevat ProgramNode nu een 'globals' lijst met alle top-level items in volgorde:
      - IncludeNode / IncludeFileNode  (#include)
      - DefineNode                     (#define)
      - EnumDefNode                    (enum definities)
      - FunctionDeclNode               (forward declarations)
      - FunctionDefNode                (functiedefinities, incl. main)
      - VarDeclNode                    (globale variabelen)
      - CommentNode                    (top-level comments)

    WAAROM 'globals' in volgorde bewaren?
      De semantic analysis verwerkt globals van boven naar beneden.
      Volgorde bepaalt of een functie al gedeclareerd is vóór gebruik.

    EDGE CASE: main() is nu gewoon een FunctionDefNode in de globals lijst.
      De semantic analysis checkt of er exact één main() aanwezig is.

    EDGE CASE: backwards-compatibiliteit met visitors die visitProgram(node)
      verwachten en node.globals itereren.
    """
    def __init__(self, globals: list = None):
        # Alle top-level items in broncode-volgorde
        self.globals = globals if globals is not None else []

    def accept(self, visitor):
        return visitor.visitProgram(self)

    def __repr__(self):
        return f"ProgramNode(globals={self.globals})"


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


# ============================================================
# ASSIGNMENT 5 — PREPROCESSOR NODES
# ============================================================

class DefineNode(ASTNode):
    """
    Een #define directive, bewaard in de AST voor volledigheid.

    Voorbeeld:
      #define bool int   →  DefineNode('bool', 'int')
      #define MAX 100    →  DefineNode('MAX', '100')
      #define GUARD      →  DefineNode('GUARD', '')

    WAAROM in de AST bewaren?
      De preprocessor heeft de substitutie al gedaan vóór de parser.
      We bewaren de DefineNode puur voor visualisatie en documentatie
      van de AST. De semantic analysis en LLVM visitor negeren hem.

    EDGE CASE: define zonder waarde → value = ''
    """
    def __init__(self, name: str, value: str):
        self.name  = name   # 'bool', 'MAX', 'GUARD'
        self.value = value  # 'int', '100', ''

    def accept(self, visitor):
        return visitor.visitDefine(self)

    def __repr__(self):
        return f"DefineNode({self.name!r} → {self.value!r})"


class IncludeFileNode(ASTNode):
    """
    Een #include "pad/naar/file.h" directive, bewaard in de AST.

    Voorbeeld:
      #include "utils/math.h"  →  IncludeFileNode('utils/math.h')

    WAAROM apart van IncludeNode (<stdio.h>)?
      IncludeNode is voor systeemheaders (<stdio.h>).
      IncludeFileNode is voor gebruikersheaders ("file.h").
      De preprocessor heeft de inhoud al ingeladen; deze node is
      puur voor AST-visualisatie.
    """
    def __init__(self, path: str):
        self.path = path   # 'utils/math.h'

    def accept(self, visitor):
        return visitor.visitIncludeFile(self)

    def __repr__(self):
        return f"IncludeFileNode({self.path!r})"


# ============================================================
# ASSIGNMENT 5 — FUNCTIE NODES
# ============================================================

class ParamNode(ASTNode):
    """
    Één parameter in een functiedefinitie of -declaratie.

    Voorbeelden:
      int x          →  ParamNode(TypeNode('int', 0), 'x')
      const float* p →  ParamNode(TypeNode('float', 1, is_const=True), 'p')
      char c         →  ParamNode(TypeNode('char', 0), 'c')

    EDGE CASE: const geldt voor het type van de parameter, niet voor
      de pointer zelf (simplified model voor onze subset).
    EDGE CASE: pass-by-reference via pointer → pointer_depth >= 1.
      De semantic analysis checkt bij aanroep of de types kloppen.
    """
    def __init__(self, param_type: TypeNode, name: str):
        self.param_type = param_type  # TypeNode
        self.name       = name        # 'x', 'ptr', 'c'

    def accept(self, visitor):
        return visitor.visitParam(self)

    def __repr__(self):
        return f"ParamNode({self.param_type}, {self.name!r})"


class FunctionDeclNode(ASTNode):
    """
    Een forward declaration van een functie.

    Voorbeeld:
      int mul(int x, int y);
        → FunctionDeclNode(
              return_type = TypeNode('int'),
              name        = 'mul',
              params      = [ParamNode(TypeNode('int'), 'x'),
                             ParamNode(TypeNode('int'), 'y')]
          )

    WAAROM forward declarations bewaren?
      De semantic analysis checkt:
        1. Dat een definitie later BESTAAT voor elke forward decl.
        2. Dat de definitie OVEREENKOMT in return type en parameters.
        3. Dat functies alleen aangeroepen worden NA declaratie/definitie.

    EDGE CASE: forward declaration in een header file → na #include
      inladen staat de FunctionDeclNode gewoon in de globals lijst.
    EDGE CASE: void return type → return_type = TypeNode('void')
    EDGE CASE: geen parameters → params = []
    """
    def __init__(self, return_type: TypeNode, name: str, params: list):
        self.return_type = return_type  # TypeNode (incl. 'void')
        self.name        = name         # 'mul', 'main', 'foo'
        self.params      = params       # lijst van ParamNode objecten

    def accept(self, visitor):
        return visitor.visitFunctionDecl(self)

    def __repr__(self):
        params_str = ', '.join(str(p) for p in self.params)
        return f"FunctionDeclNode({self.return_type} {self.name!r}({params_str}))"


class FunctionDefNode(ASTNode):
    """
    Een volledige functiedefinitie, inclusief body.

    Voorbeeld:
      int mul(int x, int y) { return x * y; }
        → FunctionDefNode(
              return_type = TypeNode('int'),
              name        = 'mul',
              params      = [ParamNode(TypeNode('int'), 'x'),
                             ParamNode(TypeNode('int'), 'y')],
              body        = BlockNode([ReturnNode(BinaryOpNode('*', ...))])
          )

    Voorbeeld (void, geen return waarde):
      void printHello() { ... }
        → FunctionDefNode(TypeNode('void'), 'printHello', [], BlockNode([...]))

    Voorbeeld (main):
      int main() { return 0; }
        → FunctionDefNode(TypeNode('int'), 'main', [], BlockNode([...]))

    EDGE CASE: main() is gewoon een FunctionDefNode. De semantic analysis
      checkt dat er exact één main() bestaat.
    EDGE CASE: recursieve aanroep → de functie roept zichzelf aan via
      FunctionCallNode met dezelfde naam. De semantic analysis moet de
      functie registreren VÓÓR de body bezocht wordt.
    EDGE CASE: void functie met return; → ReturnNode(value=None) is geldig.
    EDGE CASE: void functie zonder return → ook geldig (impliciet return).
    EDGE CASE: non-void functie zonder return → semantic warning/error.
    """
    def __init__(self, return_type: TypeNode, name: str,
                 params: list, body: BlockNode):
        self.return_type = return_type  # TypeNode (incl. 'void')
        self.name        = name         # 'mul', 'main', 'foo'
        self.params      = params       # lijst van ParamNode objecten
        self.body        = body         # BlockNode met de statements

    def accept(self, visitor):
        return visitor.visitFunctionDef(self)

    def __repr__(self):
        params_str = ', '.join(str(p) for p in self.params)
        return (f"FunctionDefNode({self.return_type} {self.name!r}"
                f"({params_str}), body={self.body})")


class ReturnNode(ASTNode):
    """
    Een return statement.

    Voorbeelden:
      return x + y;  →  ReturnNode(value=BinaryOpNode('+', ...))
      return 0;      →  ReturnNode(value=LiteralNode(0))
      return;        →  ReturnNode(value=None)

    EDGE CASE: return met waarde in void functie → semantic error.
    EDGE CASE: return met verkeerd type (bv. float in int functie) →
      semantic error of impliciete cast (afhankelijk van implementatie).
    EDGE CASE: return buiten een functie → semantic error.
    EDGE CASE: code NA return in hetzelfde blok → dead code.
      De optimalisatie visitor verwijdert alle statements na een ReturnNode.
    EDGE CASE: return in geneste if/while → springt uit de FUNCTIE,
      niet alleen uit de if/while. De LLVM visitor genereert een
      'ret' instructie die altijd uit de functie springt.
    """
    def __init__(self, value: ASTNode = None):
        self.value = value   # de returnwaarde, of None voor 'return;'

    def accept(self, visitor):
        return visitor.visitReturn(self)

    def __repr__(self):
        if self.value is None:
            return "ReturnNode(void)"
        return f"ReturnNode({self.value})"