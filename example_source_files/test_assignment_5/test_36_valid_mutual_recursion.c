// test_36_valid_mutual_recursion.c
// Verwacht: geen errors, geen warnings
// Test: wederzijdse recursie via forward declarations

#include <stdio.h>

int is_even(int n);
int is_odd(int n);

int is_even(int n) {
    if (n == 0) {
        return 1;
    }
    return is_odd(n - 1);
}

int is_odd(int n) {
    if (n == 0) {
        return 0;
    }
    return is_even(n - 1);
}

int main() {
    printf("%d\n", is_even(4));
    printf("%d\n", is_odd(3));
    return 0;
}
