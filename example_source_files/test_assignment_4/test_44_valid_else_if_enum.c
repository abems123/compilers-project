// test_valid_else_if_enum.c
// Verwacht: geen errors, geen warnings
// Test: else if met enum waarden

#include <stdio.h>

enum Dag {
    MAANDAG,
    WOENSDAG,
    VRIJDAG
};

int main() {
    enum Dag d = WOENSDAG;

    if (d == MAANDAG) {
        printf("begin van de week\n");
    } else if (d == WOENSDAG) {
        printf("midden van de week\n");
    } else if (d == VRIJDAG) {
        printf("einde van de week\n");
    } else {
        printf("weekend\n");
    }
}