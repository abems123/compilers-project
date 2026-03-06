// test_04_valid_for_loop.c
// Verwacht: geen errors, geen warnings
// Test: for lus met declaratie in init, geneste for

#include <stdio.h>

int main() {
    // for lus met declaratie in init, i++ als update
    for (int i = 0; i < 5; i++) {
        printf("%d\n", i);
    }

    // geneste for lus
    for (int x = 0; x < 3; x++) {
        for (int y = 0; y < 3; y++) {
            printf("%d %d\n", x, y);
        }
    }
}