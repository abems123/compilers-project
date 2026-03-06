// test_const_cast_float.c
// Verwacht: geen errors, geen warnings
// Test: exact het spec-voorbeeld met float

#include <stdio.h>

int main() {
    const float f = 1.0;
    const float* f_ptr = &f;
    float* non_const_f_ptr = f_ptr;  // const casting → OK
    *non_const_f_ptr = 3.14;         // f is nu gewijzigd
    printf("%f\n", f);               // 3.140000

    return 0;
}
// Verwachte output: 3.140000
