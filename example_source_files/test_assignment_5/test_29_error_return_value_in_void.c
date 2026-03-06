// test_29_error_return_value_in_void.c
// Verwacht: error — void functie 'greet' mag geen waarde teruggeven
// Test: return met waarde in een void functie

#include <stdio.h>

void greet() {
    printf("hello\n");
    return 42;
}

int main() {
    greet();
    return 0;
}
