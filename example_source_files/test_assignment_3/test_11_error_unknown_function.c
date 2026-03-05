// test_11_error_unknown_function.c
// Verwacht:
//   [ Error ] Onbekende functie 'malloc'
//   [ Error ] Onbekende functie 'myFunc'
// Test: aanroepen van functies die we niet ondersteunen

#include <stdio.h>

int main() {
    // bekende functie → ok
    printf("hello\n");

    // onbekende functies → error
    malloc(100);
    myFunc(1, 2, 3);
}
