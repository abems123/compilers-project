// test_15_valid_for_with_break_continue.c
// Verwacht: geen errors, geen warnings
// Test: break en continue in een for lus

#include <stdio.h>

int main() {
    // for lus met break
    for (int i = 0; i < 100; i++) {
        if (i > 5) {
            break;
        }
        printf("%d\n", i);
    }

    // for lus met continue
    for (int j = 0; j < 10; j++) {
        if (j == 3) {
            continue;
        }
        printf("%d\n", j);
    }
}
