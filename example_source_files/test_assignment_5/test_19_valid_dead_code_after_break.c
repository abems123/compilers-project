// test_19_valid_dead_code_after_break.c
// Verwacht: geen errors, geen warnings
// Test: dead code na break in lus wordt niet gegenereerd

#include <stdio.h>

int find_first_positive(int a, int b, int c) {
    int i = 0;
    while (i < 3) {
        if (i == 0 && a > 0) {
            break;
            int dead = 999;
        }
        if (i == 1 && b > 0) {
            break;
            printf("nooit\n");
        }
        i = i + 1;
    }
    return i;
}

int main() {
    printf("%d\n", find_first_positive(1, 2, 3));
    return 0;
}
