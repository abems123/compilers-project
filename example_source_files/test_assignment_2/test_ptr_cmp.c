// test_ptr_cmp.c
// Test: pointer vergelijkingen (p < end, p == q, p != q)
#include <stdio.h>

int main() {
    int arr[4];
    arr[0] = 100;
    arr[1] = 200;
    arr[2] = 300;
    arr[3] = 400;

    int* p = arr;
    int* end = arr + 4;

    // p < end: moet 1 zijn (true)
    printf("%d\n", p < end);

    // p == arr: moet 1 zijn (zelfde adres)
    int* q = arr;
    printf("%d\n", p == q);

    // p != end: moet 1 zijn
    printf("%d\n", p != end);

    // loop met pointer: print alle elementen
    while (p < end) {
        printf("%d\n", *p);
        p++;
    }
}
// Verwachte output:
// 1
// 1
// 1
// 100
// 200
// 300
// 400
