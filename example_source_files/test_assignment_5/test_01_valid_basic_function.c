// test_01_valid_basic_function.c
// Verwacht: geen errors, geen warnings
// Test: eenvoudige functie definitie en aanroep

#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int main() {
    int result = add(3, 4);
    printf("%d\n", result);
    return 0;
}
