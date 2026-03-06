// test_02_valid_if_else.c
// Verwacht: geen errors, geen warnings
// Test: if zonder else, if met else, else-if keten

#include <stdio.h>

int main() {
    int x = 5;

    // if zonder else
    if (x > 0) {
        printf("positief\n");
    }

    // if met else
    if (x > 10) {
        printf("groot\n");
    } else {
        printf("klein\n");
    }

    // else-if keten
    if (x > 10) {
        printf("groot\n");
    } else if (x > 5) {
        printf("middel\n");
    } else if (x > 0) {
        printf("klein positief\n");
    } else {
        printf("nul of negatief\n");
    }
}
