// test_guard_define.c
// Test: #define binnen include guard wordt maar één keer verwerkt
#include <stdio.h>
#include "mymath.h"
#include "mymath.h"  // tweede include: PI mag niet dubbel gedefinieerd worden

int add(int a, int b) {
    return a + b;
}

int main() {
    int x = PI;       // PI = 3 via #define
    printf("%d\n", x);         // verwacht: 3
    printf("%d\n", add(10, 5)); // verwacht: 15
    return 0;
}
