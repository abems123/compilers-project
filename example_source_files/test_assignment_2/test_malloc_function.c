// test_malloc_function.c
// Verwacht: geen errors, geen warnings
// Test: malloc in een functie, teruggeven als pointer, vrij maken in main

#include <stdio.h>

int* make_array(int size) {
    int* p = (int*) malloc(size * 4);
    p[0] = 100;
    p[1] = 200;
    p[2] = 300;
    return p;
}

int main() {
    int* arr = make_array(3);

    printf("%d\n", arr[0]);  // 100
    printf("%d\n", arr[1]);  // 200
    printf("%d\n", arr[2]);  // 300

    free(arr);
    return 0;
}
// Verwachte output:
// 100
// 200
// 300
