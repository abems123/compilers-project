// test_const_cast_basic.c
// Verwacht: geen errors, geen warnings
// Test: const T* toewijzen aan T* (const casting) is toegestaan

#include <stdio.h>

int main() {
    const int x = 5;
    const int* const_ptr = &x;   // const pointer naar const data
    int* nonconst_ptr = const_ptr; // const casting: const weggooien → OK

    *nonconst_ptr = 99;           // schrijven via non-const pointer → OK
    printf("%d\n", x);            // 99

    return 0;
}
// Verwachte output: 99
