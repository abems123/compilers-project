// test_unused_basic.c
// Verwacht: geen errors, geen warnings
// Test: variabele die nooit gelezen wordt krijgt geen alloca in LLVM

#include <stdio.h>

int main() {
    int used = 42;
    int unused = 99;        // nooit gelezen → geen alloca verwacht
    printf("%d\n", used);   // 42
    return 0;
}
// Verwachte output: 42
// Verwacht in LLVM: geen alloca voor 'unused'
