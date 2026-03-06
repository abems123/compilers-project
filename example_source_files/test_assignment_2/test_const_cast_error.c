// test_const_cast_error.c
// Verwacht: 1 error (*py = 20 via const pointer)
// Test: schrijven via const pointer is NIET toegestaan

#include <stdio.h>

int main() {
    const int y = 10;
    const int* py = &y;
    *py = 20;           // Error: schrijven via const pointer verboden
    printf("%d\n", y);
    return 0;
}
// Verwachte output:
// [ Error ] Kan niet schrijven via const pointer '*py'
