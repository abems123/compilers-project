// test_28_error_function_redefinition.c
// Verwacht: error — functie 'add' is al gedefinieerd
// Test: dezelfde functie twee keer definiëren

#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int add(int a, int b) {
    return a + b + 1;
}

int main() {
    printf("%d\n", add(2, 3));
    return 0;
}
