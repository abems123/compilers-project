// test_05_valid_forward_declaration.c
// Verwacht: geen errors, geen warnings
// Test: forward declaration gevolgd door definitie

#include <stdio.h>

int multiply(int x, int y);

int main() {
    printf("%d\n", multiply(6, 7));
    return 0;
}

int multiply(int x, int y) {
    return x * y;
}
