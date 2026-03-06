// test_unused_with_sideeffect.c
// Verwacht: geen errors, geen warnings
// Test: ongebruikte var met function call als RHS → call wordt WEL uitgevoerd

#include <stdio.h>

int side_effect() {
    printf("side effect!\n");  // dit moet nog steeds worden uitgevoerd
    return 42;
}

int main() {
    int x = side_effect();  // x nooit gelezen, maar side_effect() moet wel draaien
    printf("done\n");
    return 0;
}
// Verwachte output:
// side effect!
// done
