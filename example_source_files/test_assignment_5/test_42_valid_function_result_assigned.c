// test_42_valid_function_result_assigned.c
// Verwacht: geen errors, geen warnings
// Test: resultaat van functie opslaan in variabele en daarna gebruiken

#include <stdio.h>

int square(int x) {
    return x * x;
}

int main() {
    int a = square(3);
    int b = square(4);
    int c = a + b;
    printf("%d\n", c);
    return 0;
}
