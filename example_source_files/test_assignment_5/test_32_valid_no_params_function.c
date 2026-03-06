// test_32_valid_no_params_function.c
// Verwacht: geen errors, geen warnings
// Test: functie zonder parameters aanroepen

#include <stdio.h>

int get_answer() {
    return 42;
}

int main() {
    printf("%d\n", get_answer());
    return 0;
}
