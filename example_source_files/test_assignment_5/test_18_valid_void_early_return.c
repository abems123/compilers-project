// test_18_valid_void_early_return.c
// Verwacht: geen errors, geen warnings
// Test: void functie met vroege return (zonder waarde)

#include <stdio.h>

void print_positive(int x) {
    if (x <= 0) {
        return;
    }
    printf("%d\n", x);
}

int main() {
    print_positive(5);
    print_positive(-3);
    print_positive(0);
    return 0;
}
