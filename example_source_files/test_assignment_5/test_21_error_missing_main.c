// test_21_error_missing_main.c
// Verwacht: error — geen main functie gevonden
// Test: compiler moet een error geven als main ontbreekt

#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

void helper() {
    printf("ik ben geen main\n");
}
