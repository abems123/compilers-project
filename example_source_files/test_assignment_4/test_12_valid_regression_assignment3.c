// test_12_valid_regression_assignment3.c
// Verwacht: geen errors, geen warnings
// Test: assignment 3 features werken nog steeds (arrays, printf, scanf)

#include <stdio.h>

int main() {
    int arr[5];
    arr[0] = 10;
    arr[1] = 20;

    int i = 0;
    while (i < 2) {
        printf("%d\n", arr[i]);
        i = i + 1;
    }

    float f = 3.14;
    if (f > 3.0) {
        printf("groter dan 3\n");
    }
}
