// test_20_valid_define_in_function.c
// Verwacht: geen errors, geen warnings
// Test: #define waarde gebruikt binnenin functie body

#include <stdio.h>

#define FACTOR 3

int scale(int x) {
    return x * FACTOR;
}

int main() {
    printf("%d\n", scale(4));
    printf("%d\n", scale(10));
    return 0;
}
