// test_22_error_call_before_declaration.c
// Verwacht: error — functie 'helper' aangeroepen voor declaratie
// Test: functie aanroepen voor ze gedeclareerd/gedefinieerd is

#include <stdio.h>

int main() {
    int x = helper(5);
    printf("%d\n", x);
    return 0;
}

int helper(int n) {
    return n * 2;
}
