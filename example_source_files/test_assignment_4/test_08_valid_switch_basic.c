// test_08_valid_switch_basic.c
// Verwacht: geen errors, geen warnings
// Test: switch met meerdere cases en default

#include <stdio.h>

int main() {
    int x = 2;

    switch (x) {
        case 1:
            printf("een\n");
            break;
        case 2:
            printf("twee\n");
            break;
        case 3:
            printf("drie\n");
            break;
        default:
            printf("anders\n");
            break;
    }
}
