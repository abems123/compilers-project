// test_42_valid_vardecl_middle_of_block.c
// Verwacht: geen errors, geen warnings
// Test: variabele declaratie midden in een blok (niet alleen bovenaan)
// Edge case: in C89 moesten declaraties bovenaan staan, maar C99+ staat
//            declaraties overal toe. Onze compiler (C-subset) staat dit toe.
//            Voor LLVM: alloca instructies worden midden in de body geëmit,
//            niet gebundeld bovenaan — dit moet correct werken.

#include <stdio.h>

int main() {
    int x = 1;
    printf("%d\n", x);

    // declaratie midden in blok
    int y = x + 5;
    printf("%d\n", y);

    // nog een declaratie na een statement
    x = x + 1;
    int z = x * y;
    printf("%d\n", z);

    // declaratie na een if-statement
    if (x > 0) {
        printf("positief\n");
    }
    int w = z + 1;
    printf("%d\n", w);
}
