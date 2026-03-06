// test_malloc_loop.c
// Verwacht: geen errors, geen warnings
// Test: malloc + loop om te vullen en te lezen

#include <stdio.h>

int main() {
    int n = 4;
    int* data = (int*) malloc(n * 4);

    data[0] = 1;
    data[1] = 2;
    data[2] = 3;
    data[3] = 4;

    int i = 0;
    int sum = 0;
    while (i < n) {
        sum = sum + data[i];
        i++;
    }

    printf("%d\n", sum);  // 10

    free(data);
    return 0;
}
// Verwachte output: 10
