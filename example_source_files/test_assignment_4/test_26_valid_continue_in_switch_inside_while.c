// test_26_valid_continue_in_switch_inside_while.c
// Verwacht: geen errors, geen warnings
// Test: continue in een switch die BINNEN een while zit — continue hoort bij de while

#include <stdio.h>

int main() {
    int i = 0;

    while (i < 5) {
        switch (i) {
            case 3:
                i = i + 1;
                continue;
            default:
                break;
        }
        printf("%d\n", i);
        i = i + 1;
    }
}
