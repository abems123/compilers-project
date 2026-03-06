// test_11_valid_const_parameter.c
// Verwacht: geen errors, geen warnings
// Test: const parameter in functie

#include <stdio.h>

int double_it(const int x) {
    return x * 2;
}

int main() {
    printf("%d\n", double_it(7));
    return 0;
}
