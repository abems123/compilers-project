// test_26_error_forward_decl_return_mismatch.c
// Verwacht: error — forward declaration van 'compute' heeft ander return type dan definitie
// Test: inconsistentie tussen forward declaration en definitie (return type)

#include <stdio.h>

float compute(int x);

int main() {
    float result = compute(5);
    printf("%f\n", result);
    return 0;
}

int compute(int x) {
    return x * 2;
}
