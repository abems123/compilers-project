// test_33_valid_switch_fallthrough.c
// Verwacht: geen errors, geen warnings
// Test: switch met fallthrough (geen break aan het einde van een case)
// Edge case: na vertaling naar if-keten verdwijnt fallthrough — wij modelleren
//            elke case als aparte if-tak, dus fallthrough is syntactisch geldig
//            maar semantisch wordt het gewoon als losse if behandeld

#include <stdio.h>

int main() {
    int x = 2;

    // case 1 heeft geen break → in echte C: fallthrough naar case 2
    // in onze compiler: wordt vertaald naar if-keten, geen fallthrough
    switch (x) {
        case 1:
            printf("een\n");
        case 2:
            printf("twee\n");
            break;
        default:
            printf("anders\n");
            break;
    }
}
