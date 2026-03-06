// test_10_valid_break_continue_nested.c
// Verwacht: geen errors, geen warnings
// Test: break en continue in geneste lussen, break hoort bij binnenste lus

#include <stdio.h>

int main() {
    // break in binnenste lus verlaat alleen de binnenste lus
    int i = 0;
    while (i < 3) {
        int j = 0;
        while (j < 10) {
            if (j > 2) {
                break;
            }
            j = j + 1;
        }
        i = i + 1;
    }

    // continue in binnenste lus
    int x = 0;
    while (x < 5) {
        int y = 0;
        while (y < 5) {
            y = y + 1;
            if (y == 3) {
                continue;
            }
            printf("%d\n", y);
        }
        x = x + 1;
    }
}
