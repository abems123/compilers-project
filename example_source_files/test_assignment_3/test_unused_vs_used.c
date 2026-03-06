// test_unused_vs_used.c
// Verwacht: geen errors, geen warnings
// Test: mix van gebruikte en ongebruikte variabelen

#include <stdio.h>

int main() {
    int a = 1;      // gebruikt
    int b = 2;      // ongebruikt
    int c = 3;      // gebruikt
    int d = 4;      // ongebruikt
    int e = a + c;  // gebruikt (en leest a en c)

    printf("%d\n", e);  // 4
    return 0;
}
// Verwachte output: 4
// Verwacht in LLVM: alloca voor a, c, e — GEEN alloca voor b en d
