// test_23_error_wrong_param_count.c
// Verwacht: error — functie 'add' aangeroepen met verkeerd aantal argumenten
// Test: functie aanroepen met te weinig argumenten

#include <stdio.h>

int add(int a, int b) {
    return a + b;
}

int main() {
    int result = add(5);
    printf("%d\n", result);
    return 0;
}
