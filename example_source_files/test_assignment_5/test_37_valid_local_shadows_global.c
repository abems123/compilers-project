// test_37_valid_local_shadows_global.c
// Verwacht: geen errors, geen warnings
// Test: lokale variabele met dezelfde naam als globale variabele

#include <stdio.h>

int x = 100;

int get_local() {
    int x = 5;
    return x;
}

int main() {
    printf("%d\n", x);
    printf("%d\n", get_local());
    printf("%d\n", x);
    return 0;
}
