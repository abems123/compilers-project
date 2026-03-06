// test_return_valid.c
// Verwacht: geen errors, geen warnings
// Test: alle correcte return-patronen

#include <stdio.h>

// Simpele return
int double_it(int x) {
    return x * 2;
}

// if + else allebei return
int abs_val(int x) {
    if (x < 0) {
        return -x;
    } else {
        return x;
    }
}

// geneste if/else, alle takken return
int classify(int x) {
    if (x < 0) {
        return -1;
    } else {
        if (x == 0) {
            return 0;
        } else {
            return 1;
        }
    }
}

// void: geen return nodig
void print_it(int x) {
    printf("%d\n", x);
}

int main() {
    printf("%d\n", double_it(6));   // 12
    printf("%d\n", abs_val(-5));    // 5
    printf("%d\n", abs_val(3));     // 3
    printf("%d\n", classify(-10));  // -1
    printf("%d\n", classify(0));    // 0
    printf("%d\n", classify(7));    // 1
    print_it(42);                   // 42
    return 0;
}
// Verwachte output:
// 12
// 5
// 3
// -1
// 0
// 1
// 42
