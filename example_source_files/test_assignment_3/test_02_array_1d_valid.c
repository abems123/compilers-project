// test_02_array_1d_valid.c
// Verwacht: geen errors, geen warnings
// Test: 1D array declaratie zonder init, met init, toegang, assignment

#include <stdio.h>

int main() {
    // declaratie zonder initialisatie
    int arr[5];

    // declaratie met volledige initialisatie
    int values[3] = {10, 20, 30};

    // float array
    float flt[2] = {1.5, 2.5};

    // char array
    char letters[3] = {'a', 'b', 'c'};

    // array element lezen
    int x = values[0];
    int y = values[2];

    // array element schrijven
    arr[0] = 42;
    arr[4] = 99;

    // array element gebruiken in expressie
    int z = values[0] + values[1];

    // array element met variabele als index
    int i = 1;
    int w = values[i];

    // array element met expressie als index
    int v = values[i + 1];

    printf("%d\n", x);
}
