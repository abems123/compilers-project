// test_15_valid_function_with_if.c
// Verwacht: geen errors, geen warnings
// Test: functie met if/else binnenin (combinatie assignment 4 + 5)

#include <stdio.h>

int abs_val(int x) {
    if (x < 0) {
        return -x;
    } else {
        return x;
    }
}

int main() {
    printf("%d\n", abs_val(-7));
    printf("%d\n", abs_val(3));
    return 0;
}
