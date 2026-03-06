// test_ptr_diff.c
// Test: ptr - ptr (geeft aantal elementen tussen twee pointers)
#include <stdio.h>

int main() {
    int arr[6];
    arr[0] = 1;
    arr[1] = 2;
    arr[2] = 3;
    arr[3] = 4;
    arr[4] = 5;
    arr[5] = 6;

    int* begin = arr;
    int* end = arr + 6;

    // afstand van begin naar end: 6 elementen
    int len = end - begin;
    printf("%d\n", len);

    int* mid = arr + 3;

    // afstand van begin naar mid: 3
    int d1 = mid - begin;
    printf("%d\n", d1);

    // afstand van mid naar end: 3
    int d2 = end - mid;
    printf("%d\n", d2);
}
// Verwachte output:
// 6
// 3
// 3
