from antlr4 import FileStream, CommonTokenStream
from gen.MyGrammarLexer import MyGrammarLexer
from gen.MyGrammarParser import MyGrammarParser

def main():
    # This is just an example that I got by following the steps in overview_antlr.pdf
    source = FileStream("example_source_files/example_code.txt", encoding="utf-8")

    lexer = MyGrammarLexer(source)
    tokens = CommonTokenStream(lexer)

    parser = MyGrammarParser(tokens)
    tree = parser.program()  # start rule name

    print(tree.toStringTree(recog=parser))

if __name__ == "__main__":
    main()
    