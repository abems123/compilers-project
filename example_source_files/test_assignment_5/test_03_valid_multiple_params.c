// test_03_valid_multiple_params.c
// Verwacht: geen errors, geen warnings
// Test: functie met meerdere parameters van verschillende types

#include <stdio.h>

float calculate(int x, float y, int z) {
    return x + y + z;
}

int main() {
    float res = calculate(1, 2.5, 3);
    printf("%f\n", res);
    return 0;
}
