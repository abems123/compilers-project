// test_19_valid_assignment2_regression.c
// Verwacht: warnings voor impliciete conversies (char c = 3.14, etc.)
// Test: zeker zijn dat assignment 2 features niet gebroken zijn

#include <stdio.h>

int main() {
    // assignment 2 features
    const int x = 5*(3/10 + 9/10);
    float y = x*2/(2+1*2/3+x) + 8*(8/4);
    y = x + y;
    int z;
    float* flt_ptr = &y;
    char ch = 'x';
    const int* ptr_to_int = &z;

    // impliciete conversie warning (van assignment 2)
    char c = 3.14;
    int i = (int) 3.14;

    printf("%d\n", x);
}
