// test_12_valid_dead_code_after_return.c
// Verwacht: geen errors, geen warnings
// Test: dead code na return wordt niet gegenereerd (optimalisatie)

#include <stdio.h>

int get_five() {
    return 5;
    int unreachable = 99;
    printf("dit wordt nooit geprint\n");
}

int main() {
    printf("%d\n", get_five());
    return 0;
}
