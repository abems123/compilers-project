// test_02_valid_void_function.c
// Verwacht: geen errors, geen warnings
// Test: void functie zonder return waarde

#include <stdio.h>

void greet() {
    printf("hello\n");
}

int main() {
    greet();
    return 0;
}
