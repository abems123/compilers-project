# src/main/__main__.py

import argparse
from pathlib import Path

from antlr4 import InputStream, CommonTokenStream

from .gen.MyGrammarLexer   import MyGrammarLexer
from .gen.MyGrammarParser  import MyGrammarParser

from ..parser.preprocessor               import Preprocessor
from ..parser.ast_visitor                import CSTtoASTVisitor
from ..parser.constant_folding_visitor   import ConstantFoldingVisitor
from ..parser.dead_code_visitor          import DeadCodeVisitor
from ..parser.ast_dot_visitor            import ASTDotVisitor
from ..parser.semantic_analysis_visitor  import SemanticAnalysisVisitor
from ..llvm_target.llvm_visitor          import LLVMVisitor


def main():

    # --------------------------------------------------------
    # Stap 1: command line argumenten
    # --------------------------------------------------------
    arg_parser = argparse.ArgumentParser(
        description="Assignment 5 compiler: functies, headers, LLVM IR"
    )
    arg_parser.add_argument("--input",       required=True,
                            help="Pad naar het input bestand (C broncode)")
    arg_parser.add_argument("--render_ast",  required=False,
                            help="Pad naar het output .dot bestand voor AST visualisatie")
    arg_parser.add_argument("--no_folding",  action="store_true",
                            help="Zet constant folding en constant propagation uit")
    arg_parser.add_argument("--output_llvm", required=False,
                            help="Pad naar het output .ll bestand voor LLVM IR")

    args = arg_parser.parse_args()

    input_path = Path(args.input).resolve()

    # --------------------------------------------------------
    # Stap 2: preprocessor (#include + #define)
    # --------------------------------------------------------
    preprocessor = Preprocessor(base_dir=input_path.parent)
    preprocessed_source = preprocessor.process(input_path)

    if preprocessor.has_errors():
        preprocessor.print_errors()
        return

    # --------------------------------------------------------
    # Stap 3: parse → CST (nu op de preprocessed source string)
    # --------------------------------------------------------
    source = InputStream(preprocessed_source)
    lexer  = MyGrammarLexer(source)
    tokens = CommonTokenStream(lexer)
    parser = MyGrammarParser(tokens)
    cst    = parser.program()

    if parser.getNumberOfSyntaxErrors() > 0:
        print("Syntax errors gevonden: het programma is ongeldig.")
        return

    # --------------------------------------------------------
    # Stap 4: CST → AST
    # --------------------------------------------------------
    ast_visitor = CSTtoASTVisitor()
    ast = ast_visitor.visit(cst)

    # check voor fouten gevonden tijdens CST→AST vertaling
    if ast_visitor.errors:
        for e in ast_visitor.errors:
            print(e)
        return

    # --------------------------------------------------------
    # Stap 5: semantische analyse
    # --------------------------------------------------------
    semantic = SemanticAnalysisVisitor()
    ast.accept(semantic)
    semantic.print_results()

    if semantic.has_errors():
        return

    # --------------------------------------------------------
    # Stap 6: constant folding + propagation (optioneel)
    # --------------------------------------------------------
    if not args.no_folding:
        ast = ast.accept(ConstantFoldingVisitor())

    # --------------------------------------------------------
    # Stap 7: dead code eliminatie (altijd aan)
    # --------------------------------------------------------
    ast = ast.accept(DeadCodeVisitor())

    # --------------------------------------------------------
    # Stap 8: print AST (voor debugging)
    # --------------------------------------------------------
    print("\nAST:")
    print(f"  {ast}")

    # --------------------------------------------------------
    # Stap 9: render AST als .dot bestand (optioneel)
    # --------------------------------------------------------
    if args.render_ast:
        dot = ASTDotVisitor()
        ast.accept(dot)
        dot_text = dot.finalize()

        output_path = Path(args.render_ast)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(dot_text, encoding="utf-8")
        print(f"\nAST DOT geschreven naar: {args.render_ast}")

    # --------------------------------------------------------
    # Stap 10: LLVM IR genereren (optioneel)
    # --------------------------------------------------------
    if args.output_llvm:
        llvm = LLVMVisitor()
        llvm_code = ast.accept(llvm)

        output_path = Path(args.output_llvm)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(llvm_code, encoding="utf-8")
        print(f"\nLLVM IR geschreven naar: {args.output_llvm}")


if __name__ == "__main__":
    main()