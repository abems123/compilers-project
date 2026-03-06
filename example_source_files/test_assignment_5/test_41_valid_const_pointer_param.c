// test_41_valid_const_pointer_param.c
// Verwacht: geen errors, geen warnings
// Test: const pointer parameter (kan niet gewijzigd worden via pointer)

#include <stdio.h>

int read_value(const int* ptr) {
    return *ptr;
}

int main() {
    int x = 77;
    printf("%d\n", read_value(&x));
    return 0;
}
