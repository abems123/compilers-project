// test_const_no_propagate.c
// Verwacht: geen errors, geen warnings
// Test: const variabele waarvan het adres via non-const pointer genomen wordt
//       mag NIET door constant folding geïnlinend worden (waarde kan wijzigen)

#include <stdio.h>

int main() {
    const int a = 10;
    int* p = &a;         // adres van const via non-const pointer
    *p = 42;             // wijzig a via de pointer
    printf("%d\n", a);   // moet 42 zijn, NIET de gefolde waarde 10
    return 0;
}
// Verwachte output: 42
