// test_25_error_return_type_mismatch.c
// Verwacht: error — return type van 'get_int' is int maar geeft float* terug
// Test: functie geeft waarde terug die niet overeenkomt met return type

#include <stdio.h>

int get_int() {
    float x = 3.14;
    return &x;
}

int main() {
    printf("%d\n", get_int());
    return 0;
}
