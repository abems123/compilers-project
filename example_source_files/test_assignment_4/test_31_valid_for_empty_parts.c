// test_31_valid_for_empty_parts.c
// Verwacht: geen errors, geen warnings
// Test: for(;;) — lege init, lege conditie, lege update = oneindige lus met break
// Edge case: lege conditie wordt vertaald naar while(1) in de AST

#include <stdio.h>

int main() {
    // for(;;) is een oneindige lus — alleen geldig met break erin
    int x = 0;
    for (;;) {
        x = x + 1;
        if (x > 5) {
            break;
        }
    }

    // for met alleen conditie, geen init en geen update
    int i = 0;
    for (; i < 3;) {
        printf("%d\n", i);
        i = i + 1;
    }

    // for met init en conditie maar geen update
    for (int j = 0; j < 3;) {
        j = j + 1;
    }
}
