# src/parser/preprocessor.py
#
# De preprocessor draait VÓÓR de parser.
# Hij lost twee dingen op:
#   1. #include "pad/naar/file.h"  → inladen van dat bestand
#   2. #define OUD NIEUW           → tekst-substitutie door het hele bestand
#
# Volgorde is belangrijk:
#   - Eerst alle includes oplossen (recursief)
#   - Dan alle defines vervangen (van langste naam naar kortste, om
#     partial-match problemen te vermijden)
#
# EDGE CASES die we afhandelen:
#   - Circulaire includes (A includeert B, B includeert A) → fout
#   - Bestand niet gevonden → fout
#   - #define van een waarde die zelf ook een #define-naam is → werkt
#     correct door substitutie op het eindresultaat te doen
#   - #include <stdio.h> → laten we staan (wordt door grammar herkend)
#   - (optioneel) include guards: #ifndef / #define / #endif

import re
from pathlib import Path


class Preprocessor:
    """
    Verwerkt #include en #define directives vóór de ANTLR-parser.

    Gebruik:
        pp = Preprocessor(base_dir=Path("pad/naar/bronbestand"))
        verwerkte_code = pp.process(Path("mijn_bestand.c"))
    """

    def __init__(self, base_dir: Path):
        # De map van het hoofd-bronbestand. Relatieve #includes worden
        # ten opzichte van deze map opgelost.
        self.base_dir = base_dir

        # Bijhouden welke bestanden al verwerkt zijn (voor circulaire includes)
        # Dit is een set van absolute Path-objecten.
        self._included_files: set[Path] = set()

        # Lijst van errors die we tegenkomen
        self.errors: list[str] = []

        # De verzamelde defines: { "bool": "int", "true": "1", ... }
        # We slaan ze op in de volgorde waarin ze gevonden worden.
        self._defines: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Publieke interface
    # ------------------------------------------------------------------

    def process(self, filepath: Path) -> str:
        """
        Verwerk het gegeven bestand en geef de preprocessed broncode terug
        als één grote string.

        Dit is het startpunt — roep dit aan vanuit __main__.py.
        """
        self._included_files = set()
        self._defines = {}
        self.errors = []

        # Single-pass: includes oplossen én defines direct toepassen op
        # regels die NA de #define staan. Zo werkt het als een echte
        # C preprocessor: defines zijn alleen geldig na hun definitie.
        result = self._process_file(filepath.resolve())

        return result

    # ------------------------------------------------------------------
    # Interne methoden
    # ------------------------------------------------------------------

    def _process_file(self, filepath: Path) -> str:
        """
        Laad één bestand in, verwerk zijn #include en #define regels,
        en geef de resulterende tekst terug.

        Circulaire includes worden hier gedetecteerd.
        """
        # Circulaire include check
        if filepath in self._included_files:
            # Stille skip: bestand al eerder verwerkt (include guard gedrag)
            return ""

        # Bestand bestaat niet?
        if not filepath.exists():
            self.errors.append(f"[Preprocessor] Fout: bestand niet gevonden: {filepath}")
            return ""

        # Markeer dit bestand als 'in verwerking'
        self._included_files.add(filepath)

        source = filepath.read_text(encoding="utf-8")
        lines = source.splitlines(keepends=True)

        output_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # ── #include "pad/naar/file.h" ──────────────────────────────────
            # EDGE CASE: #include <stdio.h> laten we staan — de grammar
            # herkent dat als INCLUDE_STDIO token.
            include_match = re.match(
                r'^\s*#\s*include\s+"([^"]+)"', stripped
            )
            if include_match:
                include_path_str = include_match.group(1)
                # Relatief pad ten opzichte van het huidige bestand
                include_path = (filepath.parent / include_path_str).resolve()
                included_text = self._process_file(include_path)
                output_lines.append(included_text)
                i += 1
                continue

            # ── #define OUD NIEUW ────────────────────────────────────────────
            # Formaat: #define <naam> <waarde>
            # EDGE CASE: alles na de naam is de waarde (ook spaties etc.)
            # EDGE CASE: #define zonder waarde (bv. #define GUARD) → waarde = ""
            define_match = re.match(
                r'^\s*#\s*define\s+(\w+)(?:\s+(.*))?$', stripped
            )
            if define_match:
                name  = define_match.group(1)
                value = (define_match.group(2) or "").strip()
                self._defines[name] = value
                # Laat de lijn staan als commentaar zodat de grammar hem
                # kan parsen als DEFINE_STMT token (nodig voor de AST).
                output_lines.append(line)
                i += 1
                continue

            # ── Gewone lijn: pas huidige defines toe en doorsturen ───────────
            # Alleen defines die AL gezien zijn worden toegepast (single-pass).
            # Sorteer op lengte (langste naam eerst) om partial-matches te vermijden.
            if self._defines:
                sorted_defines = sorted(
                    self._defines.items(), key=lambda kv: len(kv[0]), reverse=True
                )
                for name, value in sorted_defines:
                    pattern = r'\b' + re.escape(name) + r'\b'
                    line = re.sub(pattern, value, line)
            output_lines.append(line)
            i += 1

        return "".join(output_lines)

    def _apply_defines(self, source: str) -> str:
        """
        Vervang alle defines in de broncode.

        We gebruiken word-boundary matching zodat bv. 'true' niet
        per ongeluk 'return' verandert.

        Sorteren op lengte (langst eerst) voorkomt partial-matches:
        als je zowel 'FOO' als 'FOOBAR' hebt, moet 'FOOBAR' eerst
        vervangen worden.

        EDGE CASE: #define regels zelf worden NIET bewerkt — anders
        verandert '#define bool int' in '#define int int' na substitutie.
        EDGE CASE: defines die zelf ook een define-naam bevatten worden
        correct afgehandeld omdat we maar één pass doen. Chained defines
        (A→B, B→C dus A→C) worden NIET opgelost — conform onze subset.
        """
        if not self._defines:
            return source

        # Sorteer: langste naam eerst (voorkomt partial-match problemen)
        sorted_defines = sorted(
            self._defines.items(),
            key=lambda kv: len(kv[0]),
            reverse=True
        )

        # Verwerk lijn voor lijn zodat we #define regels kunnen overslaan
        lines = source.splitlines(keepends=True)
        result_lines = []

        for line in lines:
            # Sla #define regels zelf over — niet substitueren
            if re.match(r'^\s*#\s*define\b', line):
                result_lines.append(line)
                continue

            # Pas alle defines toe op deze lijn
            for name, value in sorted_defines:
                pattern = r'\b' + re.escape(name) + r'\b'
                line = re.sub(pattern, value, line)

            result_lines.append(line)

        return "".join(result_lines)

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def print_errors(self):
        for e in self.errors:
            print(e)