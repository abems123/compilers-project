// test_43_valid_regression_all_features.c
// Verwacht: geen errors, geen warnings
// Test: regressie — alle assignment 5 features gecombineerd

#include <stdio.h>

#define MAX_VAL 50

int clamp(int x, int low, int high);
void print_clamped(int x);

int clamp(int x, int low, int high) {
    if (x < low) {
        return low;
    }
    if (x > high) {
        return high;
    }
    return x;
}

void print_clamped(int x) {
    int result = clamp(x, 0, MAX_VAL);
    printf("%d\n", result);
}

int main() {
    print_clamped(-10);
    print_clamped(25);
    print_clamped(100);
    return 0;
}
