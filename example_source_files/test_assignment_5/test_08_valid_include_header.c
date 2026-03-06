// test_08_valid_include_header.c
// Verwacht: geen errors, geen warnings
// Test: #include van een eigen header bestand

#include <stdio.h>
#include "test_08_helper.h"

int main() {
    int result = square(5);
    printf("%d\n", result);
    return 0;
}
