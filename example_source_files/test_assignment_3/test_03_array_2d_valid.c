// test_03_array_2d_valid.c
// Verwacht: geen errors, geen warnings
// Test: 2D array declaratie, initialisatie, toegang

#include <stdio.h>

int main() {
    // 2D array zonder initialisatie
    int matrix[3][4];

    // 2D array met volledige initialisatie
    int grid[2][3] = {{1, 2, 3}, {4, 5, 6}};

    // element lezen
    int x = grid[0][0];
    int y = grid[1][2];

    // element schrijven
    matrix[0][0] = 10;
    matrix[2][3] = 99;

    // element gebruiken in expressie
    int z = grid[0][1] + grid[1][0];

    // index met variabelen
    int i = 1;
    int j = 2;
    int w = grid[i][j];

    printf("%d\n", x);
}
