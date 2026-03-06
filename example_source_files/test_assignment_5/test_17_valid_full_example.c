// test_17_valid_full_example.c
// Verwacht: geen errors, geen warnings
// Test: volledig voorbeeld uit de assignment (mul + main met while + if)

#include "test_17_header.h"

int mul(int x, int y) {
    return x * y;
}

#define bool int
#define true 1
#define false 0

/*
* My program
*/
int main() {
    bool val = false;
    bool some_value = true;
    bool another_value = some_value && val;
    int x = 1;
    while (x < 10) {
        int result = mul(x, 2);
        if (x > 5) {
            result = mul(result, x);
        }
        printf("%d\n", result);
        x = x + 1;
    }
    return 0;
}
