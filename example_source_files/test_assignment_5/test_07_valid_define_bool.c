// test_07_valid_define_bool.c
// Verwacht: geen errors, geen warnings
// Test: #define voor bool/true/false (zoals in assignment voorbeeld)

#include <stdio.h>

#define bool int
#define true 1
#define false 0

int main() {
    bool val = false;
    bool some_value = true;
    bool another_value = some_value && val;
    printf("%d\n", another_value);
    return 0;
}
