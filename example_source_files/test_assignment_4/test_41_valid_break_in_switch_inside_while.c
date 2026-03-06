// test_41_valid_break_in_switch_inside_while.c
// Verwacht: geen errors, geen warnings
// Test: break in een switch die BINNEN een while zit
//       → break verlaat ALLEEN de switch, niet de while
// Edge case: de while blijft doorlopen na de switch
//            Dit verschilt van test_26 waar continue getest wordt

#include <stdio.h>

int main() {
    int i = 0;

    while (i < 5) {
        // switch met break: verlaat switch, while gaat verder
        switch (i) {
            case 2:
                printf("twee gevonden\n");
                break;
            case 4:
                printf("vier gevonden\n");
                break;
            default:
                printf("%d\n", i);
                break;
        }
        // dit wordt ALTIJD uitgevoerd, want break verlaat alleen switch
        i = i + 1;
    }
}
