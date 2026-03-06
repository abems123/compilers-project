// test_14_valid_multiple_functions.c
// Verwacht: geen errors, geen warnings
// Test: meerdere functies gedefinieerd en aangeroepen

#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int sub(int a, int b) {
    return a - b;
}

int mul(int a, int b) {
    return a * b;
}

int main() {
    printf("%d\n", add(2, 3));
    printf("%d\n", sub(10, 4));
    printf("%d\n", mul(3, 5));
    return 0;
}
