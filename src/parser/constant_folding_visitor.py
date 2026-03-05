# src/parser/constant_folding_visitor.py

from .ast_nodes import (
    LiteralNode, BinaryOpNode, UnaryOpNode,
    VariableNode, VarDeclNode, AssignNode,
    CastNode, TypeNode, BlockNode, ProgramNode
)


class ConstantFoldingVisitor:
    """
    Doet twee dingen in één pass over de AST:

    1. Constant Folding (was al aanwezig in assignment 1):
       Berekent expressies met alleen literals al op compile-time.
       Voorbeeld: 3 + 4  →  LiteralNode(7)

    2. Constant Propagation (nieuw in assignment 2):
       Houdt bij welke variabelen een bekende waarde hebben,
       en vervangt het gebruik van die variabele door de waarde.
       Voorbeeld:
         const int x = 5;
         int y = x + 3;   →   int y = 8;   (x vervangen door 5, dan 5+3 gevouwen)

    Voor constant propagation gebruiken we een 'known_values' dictionary:
       { variabele_naam: LiteralNode }

    Welke variabelen worden bijgehouden?
      - const variabelen: altijd, want die kunnen nooit veranderen
      - niet-const variabelen: ook, maar worden verwijderd zodra
        ze opnieuw geassigned worden (want dan is de waarde niet
        meer zeker op compile-time)
    """

    def __init__(self):
        # dict van variabelenaam → LiteralNode met de bekende waarde
        # Voorbeeld: {'x': LiteralNode(5, 'int'), 'y': LiteralNode(3.14, 'float')}
        self.known_values = {}

        # dict van variabelenaam → bool (is het een const variabele?)
        # We houden dit bij zodat we const variabelen nooit verwijderen
        # uit known_values, ook niet bij een assignment.
        self.is_const = {}

    # ============================================================
    # STRUCTUUR: program, block, statements
    # ============================================================

    def visitProgram(self, node):
        # bezoek de body (BlockNode) en geef een nieuwe ProgramNode terug
        new_body = node.body.accept(self)
        return ProgramNode(new_body)

    def visitBlock(self, node):
        # bezoek elk statement in volgorde
        # VOLGORDE IS BELANGRIJK: als x eerst gedeclareerd wordt en
        # daarna gebruikt, moet x al in known_values staan.
        new_statements = []
        for stmt in node.statements:
            new_stmt = stmt.accept(self)
            new_statements.append(new_stmt)
        return BlockNode(new_statements)

    def visitVarDecl(self, node):
        """
        Verwerkt een variabele declaratie.

        Stap 1: vouw de initialisatiewaarde (als die er is)
        Stap 2: als de gevouwen waarde een literal is, sla hem op
                in known_values zodat latere expressies hem kunnen
                gebruiken voor constant propagation
        Stap 3: geef een nieuwe VarDeclNode terug met de gevouwen waarde

        Voorbeeld:
          const int x = 3 + 2;
          → stap 1: 3 + 2 gevouwen naar LiteralNode(5)
          → stap 2: known_values['x'] = LiteralNode(5)
          → stap 3: VarDeclNode(TypeNode('int',...), 'x', LiteralNode(5))
        """
        # stap 1: vouw de initialisatiewaarde als die er is
        if node.value is not None:
            new_value = node.value.accept(self)
        else:
            new_value = None

        # stap 2: als de waarde na folding een literal is, sla hem op
        # Dit geldt voor ALLE variabelen (const en niet-const),
        # want ook niet-const variabelen zijn bekend tot de volgende assignment.
        if isinstance(new_value, LiteralNode):
            self.known_values[node.name] = new_value
            self.is_const[node.name] = node.var_type.is_const

        # stap 3: geef nieuwe VarDeclNode terug met gevouwen waarde
        return VarDeclNode(node.var_type, node.name, new_value)

    def visitAssign(self, node):
        """
        Verwerkt een assignment statement.

        Stap 1: vouw de rechterkant
        Stap 2: update known_values
                - als target een VariableNode is:
                    - als het een const variabele is: NIET updaten
                      (de semantic analysis zal dit later als error markeren)
                    - als het een niet-const variabele is: update de waarde,
                      of verwijder hem als de nieuwe waarde geen literal is
                - als target een dereference is (*ptr):
                    we weten niet wat er veranderd is → conservatief: doe niets
        Stap 3: geef nieuwe AssignNode terug
        """
        # stap 1: vouw de rechterkant
        new_value = node.value.accept(self)

        # stap 2: update known_values op basis van de target
        if isinstance(node.target, VariableNode):
            name = node.target.name

            # const variabelen worden NIET geüpdatet in known_values
            # (de semantic analysis zal de assignment zelf als fout markeren)
            if not self.is_const.get(name, False):
                if isinstance(new_value, LiteralNode):
                    # nieuwe waarde is bekend → update
                    self.known_values[name] = new_value
                else:
                    # nieuwe waarde is niet bekend op compile-time → verwijder
                    self.known_values.pop(name, None)

        # stap 3: geef nieuwe AssignNode terug
        # de target bezoeken we NIET voor folding (het is een lvalue, geen waarde)
        return AssignNode(node.target, new_value)

    # ============================================================
    # CONSTANT PROPAGATION: variabelen vervangen door hun waarde
    # ============================================================

    def visitVariable(self, node):
        """
        Dit is het hart van constant propagation.

        Als de variabele een bekende waarde heeft in known_values,
        vervangen we de VariableNode door een LiteralNode.
        Anders geven we de VariableNode ongewijzigd terug.

        Voorbeeld:
          known_values = {'x': LiteralNode(5, 'int')}
          visitVariable(VariableNode('x'))  →  LiteralNode(5, 'int')
          visitVariable(VariableNode('y'))  →  VariableNode('y')  (onbekend)
        """
        if node.name in self.known_values:
            return self.known_values[node.name]
        return node

    # ============================================================
    # EXPRESSIES: folding (grotendeels ongewijzigd van assignment 1)
    # ============================================================

    def visitLiteral(self, node):
        # een literal is al zo simpel als het kan → ongewijzigd teruggeven
        return node

    def visitBinaryOp(self, node):
        """
        Stap 1: bezoek de kinderen eerst (recursief)
                → dit doet ook constant propagation op variabelen
        Stap 2: als beide kinderen nu literals zijn → bereken het resultaat
        Stap 3: anders → geef een nieuwe BinaryOpNode terug met de gevouwen kinderen
        """
        # stap 1: bezoek kinderen (propagation + folding van subexpressies)
        left  = node.left.accept(self)
        right = node.right.accept(self)

        # stap 2: kunnen we berekenen?
        if isinstance(left, LiteralNode) and isinstance(right, LiteralNode):
            l = left.value
            r = right.value

            if node.op == '+':
                resultaat = l + r
            elif node.op == '-':
                resultaat = l - r
            elif node.op == '*':
                resultaat = l * r
            elif node.op == '/':
                if r == 0:
                    raise ZeroDivisionError(f"Deling door nul: {l} / {r}")
                # integer deling als beide operanden integers zijn
                if left.type_name == 'int' and right.type_name == 'int':
                    resultaat = l // r
                else:
                    resultaat = l / r
            elif node.op == '%':
                if r == 0:
                    raise ZeroDivisionError(f"Modulo door nul: {l} % {r}")
                resultaat = l % r
            elif node.op == '==':
                resultaat = int(l == r)
            elif node.op == '!=':
                resultaat = int(l != r)
            elif node.op == '<':
                resultaat = int(l < r)
            elif node.op == '>':
                resultaat = int(l > r)
            elif node.op == '<=':
                resultaat = int(l <= r)
            elif node.op == '>=':
                resultaat = int(l >= r)
            elif node.op == '&&':
                resultaat = int(bool(l) and bool(r))
            elif node.op == '||':
                resultaat = int(bool(l) or bool(r))
            elif node.op == '&':
                resultaat = l & r
            elif node.op == '|':
                resultaat = l | r
            elif node.op == '^':
                resultaat = l ^ r
            elif node.op == '<<':
                resultaat = l << r
            elif node.op == '>>':
                resultaat = l >> r
            else:
                raise ValueError(f"Onbekende operator: {node.op}")

            # bepaal het resultaattype
            # als één van beide operanden een float is, is het resultaat ook float
            result_type = 'float' if (left.type_name == 'float' or right.type_name == 'float') else 'int'
            return LiteralNode(resultaat, result_type)

        # stap 3: niet beide literals → kan niet gevouwen worden
        # geef wel de nieuwe kinderen mee (misschien konden die wel gevouwen worden)
        return BinaryOpNode(node.op, left, right)

    def visitUnaryOp(self, node):
        """
        Stap 1: bezoek het kind
        Stap 2: als het kind een literal is → bereken
        Stap 3: anders → geef een nieuwe UnaryOpNode terug

        Let op: prefix++ en suffix++ worden NIET gevouwen.
        Die hebben een side effect (ze passen de variabele aan),
        dus we kunnen ze niet zomaar vervangen door een waarde.
        """
        # stap 1
        operand = node.operand.accept(self)

        # ++ en -- hebben side effects → niet folden
        if node.op in ('prefix++', 'prefix--', 'suffix++', 'suffix--'):
            # BELANGRIJK: we checken node.operand (het ORIGINELE kind), niet operand
            # (het bezochte resultaat). Want als x in known_values staat, geeft
            # node.operand.accept(self) een LiteralNode terug, geen VariableNode meer.
            # Dan zou isinstance(operand, VariableNode) False zijn en x nooit
            # verwijderd worden uit known_values → fout resultaat bij gebruik van x erna.
            if isinstance(node.operand, VariableNode):
                self.known_values.pop(node.operand.name, None)
            return UnaryOpNode(node.op, node.operand)

        # stap 2
        if isinstance(operand, LiteralNode):
            v = operand.value

            if node.op == '-':
                resultaat = -v
            elif node.op == '+':
                resultaat = +v
            elif node.op == '!':
                resultaat = int(not bool(v))
            elif node.op == '~':
                resultaat = ~v
            elif node.op in ('&', '*'):
                # address-of en dereference kunnen niet gevouwen worden
                # want dat zijn pointer operaties → geef ongewijzigd terug
                return UnaryOpNode(node.op, operand)
            else:
                raise ValueError(f"Onbekende unaire operator: {node.op}")

            return LiteralNode(resultaat, operand.type_name)

        # stap 3
        return UnaryOpNode(node.op, operand)

    def visitCast(self, node):
        """
        Een cast kan gevouwen worden als de operand een literal is.
        Voorbeeld: (int) 3.7  →  LiteralNode(3, 'int')
        """
        operand = node.operand.accept(self)

        if isinstance(operand, LiteralNode):
            target = node.target_type.base_type

            if target == 'int':
                return LiteralNode(int(operand.value), 'int')
            elif target == 'float':
                return LiteralNode(float(operand.value), 'float')
            elif target == 'char':
                # (char) 65  →  'A'
                return LiteralNode(chr(int(operand.value)), 'char')

        # niet gevouwen → geef nieuwe CastNode terug met gevouwen operand
        return CastNode(node.target_type, operand)

    def visitType(self, node):
        # TypeNode bevat geen expressies → ongewijzigd teruggeven
        return node