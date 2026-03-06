# src/parser/symbol_table.py


class SymbolEntry:
    def __init__(self, name: str, base_type: str, pointer_depth: int,
                 is_const: bool, is_defined: bool, line: int = None,
                 is_array: bool = False, dimensions: list = None):
        self.name          = name
        self.base_type     = base_type
        self.pointer_depth = pointer_depth
        self.is_const      = is_const
        self.is_defined    = is_defined
        self.line          = line
        self.is_array      = is_array
        self.dimensions    = dimensions if dimensions is not None else []

    def type_str(self) -> str:
        const_str = "const " if self.is_const else ""
        stars     = "*" * self.pointer_depth
        if self.is_array:
            dims = ''.join(f'[{d}]' for d in self.dimensions)
            return f"{const_str}{self.base_type}{dims}"
        return f"{const_str}{self.base_type}{stars}"

    def __repr__(self):
        return f"SymbolEntry({self.name}: {self.type_str()})"


class FunctionEntry:
    """
    Één entry in de functie-tabel: alle info over één functie.
    Assignment 5 nieuw.

    Velden:
      - name         : naam van de functie ('mul', 'main', 'foo')
      - return_type  : tuple (base_type, pointer_depth) — bv. ('int', 0)
      - params       : lijst van (base_type, pointer_depth) tuples per parameter
      - is_defined   : True als er een body is (funcDef)
      - is_declared  : True als er een forward declaration is (funcDecl)
    """

    def __init__(self, name: str, return_type: tuple, params: list,
                 is_defined: bool = False, is_declared: bool = False):
        self.name        = name
        self.return_type = return_type
        self.params      = params
        self.is_defined  = is_defined
        self.is_declared = is_declared

    def signature_str(self) -> str:
        ret    = f"{'*' * self.return_type[1]}{self.return_type[0]}"
        params = ', '.join(f"{'*' * d}{t}" for t, d in self.params)
        return f"{ret} {self.name}({params})"

    def __repr__(self):
        return f"FunctionEntry({self.signature_str()})"


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, entry: SymbolEntry) -> bool:
        current_scope = self.scopes[-1]
        if entry.name in current_scope:
            return False
        current_scope[entry.name] = entry
        return True

    def lookup(self, name: str) -> SymbolEntry | None:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_current_scope(self, name: str) -> SymbolEntry | None:
        return self.scopes[-1].get(name, None)


class FunctionTable:
    """Houdt alle gedeclareerde en gedefinieerde functies bij. Assignment 5 nieuw."""

    def __init__(self):
        self._functions: dict[str, FunctionEntry] = {}

    def declare(self, entry: FunctionEntry):
        self._functions[entry.name] = entry

    def lookup(self, name: str) -> FunctionEntry | None:
        return self._functions.get(name, None)

    def all_functions(self) -> list:
        return list(self._functions.values())