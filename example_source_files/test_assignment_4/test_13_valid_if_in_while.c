// test_13_valid_if_in_while.c
// Verwacht: geen errors, geen warnings
// Test: if-statement genest in while, variabelen in beide scopes

#include <stdio.h>

int main() {
    int x = 0;

    while (x < 10) {
        if (x < 5) {
            int small = x * 2;
            printf("%d\n", small);
        } else {
            int big = x * 3;
            printf("%d\n", big);
        }
        x = x + 1;
    }
}
