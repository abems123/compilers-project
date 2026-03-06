// test_09_valid_global_local_vars.c
// Verwacht: geen errors, geen warnings
// Test: globale en lokale variabelen samen

#include <stdio.h>

int global_count = 0;

void increment() {
    global_count = global_count + 1;
}

int main() {
    int local = 10;
    increment();
    increment();
    printf("%d %d\n", global_count, local);
    return 0;
}
