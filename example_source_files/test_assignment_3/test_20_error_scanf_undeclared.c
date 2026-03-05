// test_20_error_scanf_undeclared.c
// Verwacht:
//   [ Error ] gebruik van niet-gedeclareerde variabele 'ghost'
// Test: scanf met een niet-gedeclareerde variabele

#include <stdio.h>

int main() {
    // ghost is niet gedeclareerd
    scanf("%d", &ghost);
}
