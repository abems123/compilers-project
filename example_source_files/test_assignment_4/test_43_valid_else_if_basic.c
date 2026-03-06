// test_valid_else_if_basic.c
// Verwacht: geen errors, geen warnings
// Test: else if keten met meerdere takken

#include <stdio.h>

int main() {
    int x = 5;

    if (x < 0) {
        printf("negatief\n");
    } else if (x == 0) {
        printf("nul\n");
    } else if (x < 10) {
        printf("klein positief\n");
    } else {
        printf("groot positief\n");
    }
}