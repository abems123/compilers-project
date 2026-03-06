// test_11_valid_scope_in_switch.c
// Verwacht: geen errors, geen warnings
// Test: variabele declaratie in switch via anonieme scope

#include <stdio.h>

int main() {
    int x = 2;

    switch (x) {
        case 1: {
            int a = 10;
            printf("%d\n", a);
            break;
        }
        case 2: {
            int a = 20;
            printf("%d\n", a);
            break;
        }
        default: {
            int a = 0;
            printf("%d\n", a);
            break;
        }
    }
}
