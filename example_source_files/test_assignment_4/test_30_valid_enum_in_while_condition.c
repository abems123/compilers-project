// test_30_valid_enum_in_while_condition.c
// Verwacht: geen errors, geen warnings
// Test: enum label als grenswaarde in while conditie

#include <stdio.h>

enum Limit {
    MIN,
    MAX
};

int main() {
    int i = MIN;

    while (i < 10) {
        printf("%d\n", i);
        i = i + 1;
    }
}
