// test_10_valid_pass_by_pointer.c
// Verwacht: geen errors, geen warnings
// Test: pass-by-reference via pointer parameter

#include <stdio.h>

void double_value(int* x) {
    *x = *x * 2;
}

int main() {
    int val = 5;
    double_value(&val);
    printf("%d\n", val);
    return 0;
}
