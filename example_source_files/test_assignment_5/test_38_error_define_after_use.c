// test_38_error_define_after_use.c
// Verwacht: error — MYVAL gebruikt voor #define
// Test: #define staat na het gebruik ervan (preprocessor verwerkt top-to-bottom)

#include <stdio.h>

int main() {
    int x = MYVAL;
    printf("%d\n", x);
    return 0;
}

#define MYVAL 42
