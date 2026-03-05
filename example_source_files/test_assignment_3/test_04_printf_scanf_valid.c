// test_04_printf_scanf_valid.c
// Verwacht: geen errors, geen warnings
// Test: printf en scanf met alle format codes, meerdere argumenten

#include <stdio.h>

int main() {
    int i = 42;
    float f = 3.14;
    char c = 'A';

    // printf zonder extra argumenten
    printf("Hello World\n");

    // printf met %d
    printf("%d\n", i);

    // printf met %f
    printf("%f\n", f);

    // printf met %c
    printf("%c\n", c);

    // printf met meerdere argumenten
    printf("int: %d, float: %f\n", i, f);

    // printf met %x (hexadecimaal)
    printf("%x\n", i);

    // printf met %% (literal procent teken)
    printf("100%%\n");

    // printf met breedte specifier
    printf("%5d\n", i);

    // scanf met &variabele
    int x;
    scanf("%d", &x);

    // scanf met meerdere argumenten
    float y;
    scanf("%d %f", &x, &y);
}
