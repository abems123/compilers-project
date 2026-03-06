// test_31_valid_define_as_typename.c
// Verwacht: geen errors, geen warnings
// Test: #define maakt een alias voor een bestaand type (zoals bool → int)

#include <stdio.h>

#define myint int

myint add(myint a, myint b) {
    return a + b;
}

int main() {
    myint x = 10;
    myint y = 20;
    printf("%d\n", add(x, y));
    return 0;
}
