// test_35_valid_multiple_forward_decls.c
// Verwacht: geen errors, geen warnings
// Test: meerdere identieke forward declarations van dezelfde functie (toegestaan)

#include <stdio.h>

int foo(int x);
int foo(int x);

int main() {
    printf("%d\n", foo(3));
    return 0;
}

int foo(int x) {
    return x + 1;
}
