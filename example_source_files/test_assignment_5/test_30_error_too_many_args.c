// test_30_error_too_many_args.c
// Verwacht: error — functie 'negate' aangeroepen met te veel argumenten
// Test: functie aanroepen met te veel argumenten

#include <stdio.h>

int negate(int x) {
    return -x;
}

int main() {
    int result = negate(5, 10);
    printf("%d\n", result);
    return 0;
}
