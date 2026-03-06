// test_guard_basic.c
// Test: header twee keer includen → geen duplicate declaration error
#include <stdio.h>
#include "mylib.h"
#include "mylib.h"  // tweede include: mag geen fout geven door include guard

int square(int x) {
    return x * x;
}

int double_val(int x) {
    return x * 2;
}

int main() {
    printf("%d\n", square(5));     // verwacht: 25
    printf("%d\n", double_val(7)); // verwacht: 14
    return 0;
}
