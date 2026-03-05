# src/parser/symbol_table.py


class SymbolEntry:
    """
    Één entry in de symbol table: alle info over één variabele.

    Voorbeeld voor  const int* x = 5 :
      SymbolEntry(
          name         = 'x',
          base_type    = 'int',
          pointer_depth = 1,
          is_const     = True,
          is_defined   = True,   ← heeft een initialisatiewaarde
          line         = 3
      )
    """

    def __init__(self, name: str, base_type: str, pointer_depth: int,
                 is_const: bool, is_defined: bool, line: int = None):
        self.name          = name
        self.base_type     = base_type      # 'int', 'float', 'char'
        self.pointer_depth = pointer_depth  # 0 = geen pointer, 1 = *, 2 = **
        self.is_const      = is_const       # is de waarde waarnaar gewezen wordt const?
        self.is_defined    = is_defined     # heeft de variabele een waarde? (int x vs int x = 5)
        self.line          = line           # regelnummer in de broncode (voor foutmeldingen)

    def type_str(self):
        """Geeft een leesbare type string terug voor in foutmeldingen."""
        const_str = "const " if self.is_const else ""
        stars     = "*" * self.pointer_depth
        return f"{const_str}{self.base_type}{stars}"

    def __repr__(self):
        return f"SymbolEntry({self.name}: {self.type_str()})"


class SymbolTable:
    """
    De symbol table houdt alle gedeclareerde variabelen bij, per scope.

    Scopes werken als een stapel (stack):
      - bij het binnengaan van een blok { ... } → push een nieuwe scope
      - bij het verlaten van een blok }         → pop de scope
      - bij opzoeken van een variabele           → zoek van boven naar beneden

    Voorbeeld met geneste scopes:
      scope 0 (globaal): { x: int }
      scope 1 (main):    { y: float, z: char }

      opzoeken van 'x' in scope 1 → niet gevonden in scope 1
                                   → gevonden in scope 0 ✓

    Momenteel heeft assignment 2 maar één scope (main),
    maar de structuur is klaar voor toekomstige geneste scopes.
    """

    def __init__(self):
        # de stack van scopes: elke scope is een dict van naam → SymbolEntry
        # we beginnen met één lege globale scope
        self.scopes = [{}]

    def push_scope(self):
        """Maak een nieuwe scope aan (bij het binnengaan van een blok)."""
        self.scopes.append({})

    def pop_scope(self):
        """Verwijder de huidige scope (bij het verlaten van een blok)."""
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(self, entry: SymbolEntry) -> bool:
        """
        Declareer een variabele in de HUIDIGE (binnenste) scope.

        Geeft True terug als de declaratie succesvol was.
        Geeft False terug als de variabele al gedeclareerd was in deze scope
        (= redeclaratie error).

        Let op: een variabele in een buitenste scope mag je wél opnieuw
        declareren in een binnenste scope (shadowing). We checken dus alleen
        de huidige scope.
        """
        current_scope = self.scopes[-1]

        if entry.name in current_scope:
            # al gedeclareerd in deze scope → redeclaratie error
            return False

        current_scope[entry.name] = entry
        return True

    def lookup(self, name: str) -> SymbolEntry | None:
        """
        Zoek een variabele op, van de binnenste naar de buitenste scope.

        Geeft de SymbolEntry terug als gevonden, anders None.
        """
        # loop van boven (binnenste scope) naar beneden (buitenste scope)
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_current_scope(self, name: str) -> SymbolEntry | None:
        """
        Zoek een variabele op ALLEEN in de huidige scope.
        Gebruikt voor redeclaratie checks.
        """
        return self.scopes[-1].get(name, None)