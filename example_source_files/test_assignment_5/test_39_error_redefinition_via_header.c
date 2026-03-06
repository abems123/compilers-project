// test_39_error_redefinition_via_header.c
// Verwacht: error — functie 'helper' is al gedefinieerd (via header)
// Test: redefinitie van een functie die al via een header gedefinieerd is

#include <stdio.h>
#include "test_39_helper.h"

int helper(int x) {
    return x + 99;
}

int main() {
    printf("%d\n", helper(1));
    return 0;
}
