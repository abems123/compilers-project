// test_guard_ifdef.c
// Test: #ifdef (alleen compileren als macro WEL gedefinieerd is)
#include <stdio.h>

#define DEBUG 1

int main() {
    int x = 42;

#ifdef DEBUG
    printf("%d\n", x);  // verwacht: 42 (want DEBUG is gedefinieerd)
#endif

    return 0;
}
