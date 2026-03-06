// test_34_valid_early_return_in_if.c
// Verwacht: geen errors, geen warnings
// Test: vroege return in if-tak, daarna nog code bereikbaar via else-tak

#include <stdio.h>

int classify(int x) {
    if (x > 0) {
        return 1;
    }
    if (x < 0) {
        return -1;
    }
    return 0;
}

int main() {
    printf("%d\n", classify(10));
    printf("%d\n", classify(-5));
    printf("%d\n", classify(0));
    return 0;
}
