// test_malloc_basic.c
// Verwacht: geen errors, geen warnings
// Test: malloc, schrijven en lezen via pointer indexering, free

#include <stdio.h>

int main() {
    int* arr = (int*) malloc(5 * 4);

    arr[0] = 10;
    arr[1] = 20;
    arr[2] = 30;
    arr[3] = 40;
    arr[4] = 50;

    printf("%d\n", arr[0]);  // 10
    printf("%d\n", arr[2]);  // 30
    printf("%d\n", arr[4]);  // 50

    free(arr);
    return 0;
}
// Verwachte output:
// 10
// 30
// 50
