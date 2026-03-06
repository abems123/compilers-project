// test_03_valid_while.c
// Verwacht: geen errors, geen warnings
// Test: basis while lus, while met break, while met continue

#include <stdio.h>

int main() {
    int i = 0;

    // basis while
    while (i < 5) {
        printf("%d\n", i);
        i = i + 1;
    }

    // while met break
    int j = 0;
    while (j < 100) {
        if (j > 3) {
            break;
        }
        j = j + 1;
    }

    // while met continue
    int k = 0;
    while (k < 10) {
        k = k + 1;
        if (k == 5) {
            continue;
        }
        printf("%d\n", k);
    }
}
