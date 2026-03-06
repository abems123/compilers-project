// test_32_valid_switch_no_default.c
// Verwacht: geen errors, geen warnings
// Test: switch zonder default clause is geldig
// Edge case: als geen enkel case matcht en er is geen default, gebeurt er niets

#include <stdio.h>

int main() {
    int x = 5;

    // switch zonder default
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
    }
    // geen match, geen default → geen output, geen error
}
