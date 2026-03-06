// test_24_error_wrong_param_type.c
// Verwacht: error — verkeerd argument type bij aanroep van 'takes_int'
// Test: functie aanroepen met verkeerd parameter type

#include <stdio.h>

int takes_int(int x) {
    return x + 1;
}

int main() {
    int* ptr = 0;
    int result = takes_int(ptr);
    printf("%d\n", result);
    return 0;
}
