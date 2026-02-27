# src/main/__main__.py

# argparse is een ingebouwde Python library om command line
# argumenten te lezen. Zo kan je bv. --input en --render_ast
# meegeven wanneer je het programma uitvoert.
import argparse

# ANTLR klassen om de input te lezen en tokens te maken
from antlr4 import FileStream, CommonTokenStream

from .gen.assignment_1Lexer import assignment_1Lexer
from .gen.assignment_1Parser import assignment_1Parser
from ..parser.ast_visitor import CSTtoASTVisitor
from ..parser.constant_folding_visitor import ConstantFoldingVisitor


def main():

    # --------------------------------------------------------
    # Stap 1: lees de command line argumenten
    # --------------------------------------------------------
    # ArgumentParser maakt een object dat de argumenten beheert.
    # description is wat getoond wordt bij --help.

    arg_parser = argparse.ArgumentParser(
        description="Assignment 1 compiler: expression parser"
    )

    # --input is verplicht: het pad naar het input bestand
    arg_parser.add_argument(
        "--input",
        required=True,
        help="Pad naar het input bestand"
    )

    # --render_ast is optioneel: pad naar het output dot bestand
    # Als je dit niet meegeeft, wordt de AST niet gevisualiseerd
    arg_parser.add_argument(
        "--render_ast",
        required=False,
        help="Pad naar het output dot bestand voor de AST visualisatie"
    )

    # --no_folding is optioneel: zet constant folding uit
    # Handig voor testen: zo kan je de AST voor en na vergelijken
    arg_parser.add_argument(
        "--no_folding",
        action="store_true",
        help="Zet constant folding uit"
    )

    # Verwerk de argumenten
    args = arg_parser.parse_args()

    # --------------------------------------------------------
    # Stap 2: lees het input bestand en maak de CST
    # --------------------------------------------------------
    # FileStream leest het bestand in
    source = FileStream(args.input, encoding="utf-8")

    # De lexer splitst de tekst op in tokens
    # Voorbeeld: "3 + 4" → [INTEGER(3), PLUS, INTEGER(4)]
    lexer = assignment_1Lexer(source)
    tokens = CommonTokenStream(lexer)

    # De parser zet de tokens om in een CST
    parser = assignment_1Parser(tokens)
    cst = parser.program()  # 'program' is onze startegel

    # --------------------------------------------------------
    # Stap 3: zet de CST om naar onze eigen AST
    # --------------------------------------------------------
    ast_builder = CSTtoASTVisitor()

    # visit() start de visitor op de wortel van de CST
    # Het resultaat is een lijst van ASTNodes (één per expressie)
    ast_nodes = ast_builder.visit(cst)

    # --------------------------------------------------------
    # Stap 4: constant folding (optioneel)
    # --------------------------------------------------------
    # Als --no_folding NIET meegegeven is, voeren we de
    # optimalisatie uit
    if not args.no_folding:
        folder = ConstantFoldingVisitor()

        # Vouw elke expressie apart
        ast_nodes = [node.accept(folder) for node in ast_nodes]

    # --------------------------------------------------------
    # Stap 5: print het resultaat (tijdelijk, voor debugging)
    # --------------------------------------------------------
    # Later vervangen we dit door de Graphviz visualisatie.
    # Voor nu printen we gewoon de knopen zodat je kan zien
    # of alles werkt.
    print("AST knopen:")
    for node in ast_nodes:
        print(f"  {node}")

    # --------------------------------------------------------
    # Stap 6: render de AST als dot bestand (optioneel)
    # --------------------------------------------------------
    # Dit doen we in de volgende stap wanneer we de
    # Graphviz visitor schrijven.
    if args.render_ast:
        print(f"\nTODO: AST renderen naar {args.render_ast}")


if __name__ == "__main__":
    main()