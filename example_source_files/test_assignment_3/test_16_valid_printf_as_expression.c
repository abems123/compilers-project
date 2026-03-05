// test_16_valid_printf_as_expression.c
// Verwacht: geen errors, geen warnings
// Test: de return waarde van printf gebruiken (printf returnt int)

#include <stdio.h>

int main() {
    // printf return waarde opslaan
    int n = printf("hello\n");

    // printf return waarde in expressie
    int m = printf("x\n") + 1;
}
