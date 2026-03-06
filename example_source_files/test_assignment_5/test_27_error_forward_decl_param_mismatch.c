// test_27_error_forward_decl_param_mismatch.c
// Verwacht: error — forward declaration van 'compute' heeft ander aantal parameters dan definitie
// Test: inconsistentie tussen forward declaration en definitie (parameters)

#include <stdio.h>

int compute(int x, int y);

int main() {
    printf("%d\n", compute(3, 4));
    return 0;
}

int compute(int x) {
    return x * 2;
}
