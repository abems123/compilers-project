// test_07_valid_enum_arithmetic.c
// Verwacht: geen errors, geen warnings
// Test: rekenen met enum labels (ze zijn int)

#include <stdio.h>

enum Direction {
    NORTH,
    EAST,
    SOUTH,
    WEST
};

int main() {
    int a = NORTH + SOUTH;  // 0 + 2 = 2
    int b = EAST * WEST;    // 1 * 3 = 3
    int c = SOUTH - NORTH;  // 2 - 0 = 2
    int d = WEST / EAST;    // 3 / 1 = 3

    printf("%d\n", a);
    printf("%d\n", b);
    printf("%d\n", c);
    printf("%d\n", d);

    int i = NORTH;
    while (i < WEST) {
        printf("%d\n", i);
        i = i + 1;
    }
}