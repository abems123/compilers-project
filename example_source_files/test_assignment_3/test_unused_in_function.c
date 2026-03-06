// test_unused_in_function.c
// Verwacht: geen errors, geen warnings
// Test: ongebruikte variabele in een functie wordt weggeoptimaliseerd

#include <stdio.h>

int compute(int n) {
    int result = n * 2;     // gebruikt: staat in return
    int garbage = n + 100;  // nooit gelezen → geen alloca
    int final = result + 1; // gebruikt: staat in return
    return final;
}

int main() {
    printf("%d\n", compute(3));   // 7
    printf("%d\n", compute(10));  // 21
    return 0;
}
// Verwachte output:
// 7
// 21
// Verwacht in LLVM: geen alloca voor 'garbage'
