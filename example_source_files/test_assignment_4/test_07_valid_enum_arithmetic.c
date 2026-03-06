#include <stdio.h>

enum Direction {
    NORTH,
    EAST,
    SOUTH,
    WEST
};

int main() {
    int a = NORTH + SOUTH;
    int b = EAST * WEST;
    int c = SOUTH - NORTH;
    int d = WEST / EAST;

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
