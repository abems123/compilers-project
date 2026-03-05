# src/main/__main__.py

import argparse
from pathlib import Path

from antlr4 import FileStream, CommonTokenStream

# BELANGRIJK: genereer de parser eerst met:
# java -jar antlr-4.13.2-complete.jar -Dlanguage=Python3 -visitor grammars/assignment_2.g4 -o src/main/gen
from .gen.MyGrammarLexer   import MyGrammarLexer
from .gen.MyGrammarParser  import MyGrammarParser

from ..parser.ast_visitor                import CSTtoASTVisitor
from ..parser.constant_folding_visitor   import ConstantFoldingVisitor
from ..parser.ast_dot_visitor            import ASTDotVisitor
from ..parser.semantic_analysis_visitor  import SemanticAnalysisVisitor


def main():

    # --------------------------------------------------------
    # Stap 1: lees de command line argumenten
    # --------------------------------------------------------
    arg_parser = argparse.ArgumentParser(
        description="Assignment 2 compiler: types and variables"
    )

    arg_parser.add_argument(
        "--input",
        required=True,
        help="Pad naar het input bestand (C broncode)"
    )

    arg_parser.add_argument(
        "--render_ast",
        required=False,
        help="Pad naar het output .dot bestand voor AST visualisatie"
    )

    arg_parser.add_argument(
        "--no_folding",
        action="store_true",
        help="Zet constant folding en constant propagation uit"
    )

    args = arg_parser.parse_args()

    # --------------------------------------------------------
    # Stap 2: lees het input bestand en maak de CST
    # --------------------------------------------------------
    source = FileStream(args.input, encoding="utf-8")
    lexer  = MyGrammarLexer(source)
    tokens = CommonTokenStream(lexer)

    parser = MyGrammarParser(tokens)
    cst    = parser.program()

    # stop meteen als er syntax fouten zijn
    if parser.getNumberOfSyntaxErrors() > 0:
        print("Syntax errors gevonden: het programma is ongeldig.")
        return

    # --------------------------------------------------------
    # Stap 3: zet de CST om naar onze eigen AST
    # --------------------------------------------------------
    ast_builder = CSTtoASTVisitor()
    ast = ast_builder.visit(cst)

    # --------------------------------------------------------
    # Stap 4: semantische analyse
    # --------------------------------------------------------
    # De semantic analysis loopt VOOR constant folding,
    # zodat we de originele variabelenamen en types nog zien.
    # (Na folding zijn variabelen soms al vervangen door literals.)
    semantic = SemanticAnalysisVisitor()
    ast.accept(semantic)
    semantic.print_results()

    # stop als er semantische fouten zijn
    if semantic.has_errors():
        return

    # --------------------------------------------------------
    # Stap 5: constant folding + propagation (optioneel)
    # --------------------------------------------------------
    if not args.no_folding:
        folder = ConstantFoldingVisitor()
        ast = ast.accept(folder)

    # --------------------------------------------------------
    # Stap 6: print het resultaat (voor debugging)
    # --------------------------------------------------------
    print("\nAST:")
    print(f"  {ast}")

    # --------------------------------------------------------
    # Stap 7: render de AST als .dot bestand (optioneel)
    # --------------------------------------------------------
    if args.render_ast:
        dot = ASTDotVisitor()
        ast.accept(dot)
        dot_text = dot.finalize()

        output_path = Path(args.render_ast)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(dot_text)

        print(f"\nAST DOT geschreven naar: {args.render_ast}")


if __name__ == "__main__":
    main()