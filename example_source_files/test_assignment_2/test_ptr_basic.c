// test_ptr_basic.c
// Test: p + int, p - int, p++, p--
#include <stdio.h>

int main() {
    int arr[5];
    arr[0] = 10;
    arr[1] = 20;
    arr[2] = 30;
    arr[3] = 40;
    arr[4] = 50;

    int* p = arr;

    // p + 2: moet element op index 2 pakken (30)
    int* q = p + 2;
    printf("%d\n", *q);

    // p - 1 na ophogen: p++ zet p naar index 1, dan p-1 = index 0 (10)
    p++;
    int* r = p - 1;
    printf("%d\n", *r);

    // *p na p++: index 1 (20)
    printf("%d\n", *p);

    // p-- zet p terug naar index 0 (10)
    p--;
    printf("%d\n", *p);
}
// Verwachte output:
// 30
// 10
// 20
// 10
