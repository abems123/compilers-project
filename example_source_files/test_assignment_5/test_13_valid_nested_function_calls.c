// test_13_valid_nested_function_calls.c
// Verwacht: geen errors, geen warnings
// Test: geneste functie aanroepen f(g(x))

#include <stdio.h>

int add_one(int x) {
    return x + 1;
}

int triple(int x) {
    return x * 3;
}

int main() {
    int result = triple(add_one(4));
    printf("%d\n", result);
    return 0;
}
