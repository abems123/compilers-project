// test_14_valid_multiple_enums.c
// Verwacht: geen errors, geen warnings
// Test: meerdere enum definities, labels van beide enums tegelijk gebruiken

#include <stdio.h>

enum Color {
    RED,
    GREEN,
    BLUE
};

enum Size {
    SMALL,
    MEDIUM,
    LARGE
};

int main() {
    enum Color c = GREEN;
    enum Size s = LARGE;

    int combo = c + s;
    printf("%d\n", combo);

    if (c == GREEN) {
        if (s == LARGE) {
            printf("groot en groen\n");
        }
    }
}
