# Compilers Project 2026
This repository contains Group 5’s Compilers course project. We are building a compiler for a subset of the C language. For more details, see the project description [here](https://github.com/abems123/UAntwerpenResources/tree/main/Semester%204/Compilers/Projects).

# Commands
## 1. Generate the parser and visitor
Generate the parser and visitor classes in Python using the following command:
``` bash
java -jar antlr-4.12.0-complete.jar -Dlanguage=Python3 MyGrammar.g4 -visitor
```

This will generate: - `MyGrammarLexer.py` - `MyGrammarParser.py` -
`MyGrammarVisitor.py` - and supporting files


## 2. Running the compiler
Example:
``` bash
python3 -m src.main --input example.c
```

Optional flags:

``` bash
--no_folding              # Disable constant folding
--render_ast file.dot     # Generate AST in Graphviz format
```
# Notes
Always comment your code step per step in a clear language so that the other group members can understand your code, this way it will be easy for all of us to participate in the development of our compiler.

Please don't use AI all the time to generate code or grammar rules. AI should help us understand hard concepts and make it easier for us to grasp new things, but it shouldn't generate the whole project while we do nothing.