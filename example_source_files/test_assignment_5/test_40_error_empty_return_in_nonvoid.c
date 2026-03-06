// test_40_error_empty_return_in_nonvoid.c
// Verwacht: error — return zonder waarde in niet-void functie 'get_num'
// Test: return zonder waarde in een functie met int return type

#include <stdio.h>

int get_num() {
    return;
}

int main() {
    printf("%d\n", get_num());
    return 0;
}
