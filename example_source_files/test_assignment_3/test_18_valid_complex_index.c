// test_18_valid_complex_index.c
// Verwacht: geen errors, geen warnings
// Test: complexe expressies als array index

#include <stdio.h>

int main() {
    int arr[10];
    int i = 3;
    int j = 2;

    // binaire expressie als index
    int a = arr[i + j];
    int b = arr[i * 2];
    int c = arr[i - 1];

    // geneste array access als index
    int indices[3] = {0, 1, 2};
    int d = arr[indices[0]];

    // vergelijking als index (geeft 0 of 1)
    int e = arr[i > j];

    printf("%d\n", a);
}
