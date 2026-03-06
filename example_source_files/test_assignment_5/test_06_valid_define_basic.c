// test_06_valid_define_basic.c
// Verwacht: geen errors, geen warnings
// Test: eenvoudige #define tekstvervaging

#include <stdio.h>

#define MAX 100
#define MIN 0

int main() {
    int x = MAX;
    int y = MIN;
    printf("%d %d\n", x, y);
    return 0;
}
