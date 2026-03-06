// test_29_valid_infinite_while.c
// Verwacht: geen errors, geen warnings
// Test: while (1) met break is geldig (oneindige lus met uitgang)

#include <stdio.h>

int main() {
    int x = 0;

    while (1) {
        x = x + 1;
        if (x > 10) {
            break;
        }
        printf("%d\n", x);
    }
}
