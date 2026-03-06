// test_16_valid_function_with_while.c
// Verwacht: geen errors, geen warnings
// Test: functie met while-lus binnenin (combinatie assignment 4 + 5)

#include <stdio.h>

int sum_up_to(int n) {
    int total = 0;
    int i = 1;
    while (i <= n) {
        total = total + i;
        i = i + 1;
    }
    return total;
}

int main() {
    printf("%d\n", sum_up_to(10));
    return 0;
}
