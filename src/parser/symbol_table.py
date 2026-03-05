# src/parser/symbol_table.py


class SymbolEntry:
    """
    Één entry in de symbol table: alle info over één variabele.

    Assignment 3 uitbreiding:
      - is_array    : True als de variabele een array is
      - dimensions  : lijst van ints voor de array dimensies, bv. [3] of [2,4]
                      leeg als is_array=False

    Voorbeeld voor  int arr[3] :
      SymbolEntry(name='arr', base_type='int', pointer_depth=0,
                  is_const=False, is_defined=True,
                  is_array=True, dimensions=[3])

    Voorbeeld voor  const int* p = &z :
      SymbolEntry(name='p', base_type='int', pointer_depth=1,
                  is_const=True, is_defined=True,
                  is_array=False, dimensions=[])
    """

    def __init__(self, name: str, base_type: str, pointer_depth: int,
                 is_const: bool, is_defined: bool, line: int = None,
                 is_array: bool = False, dimensions: list = None):
        self.name          = name
        self.base_type     = base_type
        self.pointer_depth = pointer_depth
        self.is_const      = is_const
        self.is_defined    = is_defined
        self.line          = line

        # NIEUW in assignment 3
        self.is_array   = is_array
        # dimensions is altijd een lijst — nooit None na initialisatie
        self.dimensions = dimensions if dimensions is not None else []

    def type_str(self) -> str:
        """Geeft een leesbare type string terug voor in foutmeldingen."""
        const_str = "const " if self.is_const else ""
        stars     = "*" * self.pointer_depth
        if self.is_array:
            dims = ''.join(f'[{d}]' for d in self.dimensions)
            return f"{const_str}{self.base_type}{dims}"
        return f"{const_str}{self.base_type}{stars}"

    def __repr__(self):
        return f"SymbolEntry({self.name}: {self.type_str()})"


class SymbolTable:
    """
    De symbol table houdt alle gedeclareerde variabelen bij, per scope.
    Ongewijzigd van assignment 2 — alleen SymbolEntry is uitgebreid.
    """

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