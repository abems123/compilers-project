// test_09_valid_switch_with_enum.c
// Verwacht: geen errors, geen warnings
// Test: switch op een enum variabele

#include <stdio.h>

enum Status {
    READY,
    BUSY,
    OFFLINE
};

int main() {
    enum Status s = BUSY;

    switch (s) {
        case READY:
            printf("klaar\n");
            break;
        case BUSY:
            printf("bezig\n");
            break;
        case OFFLINE:
            printf("offline\n");
            break;
        default:
            printf("onbekend\n");
            break;
    }
}
