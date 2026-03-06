// test_33_valid_function_call_as_arg.c
// Verwacht: geen errors, geen warnings
// Test: functie aanroep als argument aan een andere functie meegeven

#include <stdio.h>

int double_it(int x) {
    return x * 2;
}

int add_one(int x) {
    return x + 1;
}

int main() {
    printf("%d\n", double_it(add_one(4)));
    printf("%d\n", add_one(double_it(3)));
    return 0;
}
