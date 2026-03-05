// test_13_valid_full_example.c
// Verwacht: geen errors, geen warnings
// Test: het voorbeeld uit de opdracht zelf

#include <stdio.h>

/*
 * My program
 */

int main() {
    int x = 5*(3/10 + 9/10);
    float y = x*2/( 2+1 * 2/3 +x) +8 * (8/4);
    float result = x + y; //calculate the result
    printf("Result:\n");
    printf("Number: %f\n", result); //show the result
}
