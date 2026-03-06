// test_return_warn_else_if.c
// Verwacht: 1 warning (incomplete_chain)
// Test: else-if keten zonder finale else

#include <stdio.h>

// FOUT: else-if zonder afsluitende else → derde pad heeft geen return
int incomplete_chain(int x) {
    if (x > 0) {
        return 1;
    } else {
        if (x < 0) {
            return -1;
        }
        // x == 0: geen return!
    }
}

// GOED: else-if keten MET afsluitende else
int complete_chain(int x) {
    if (x > 0) {
        return 1;
    } else {
        if (x < 0) {
            return -1;
        } else {
            return 0;
        }
    }
}

int main() {
    printf("%d\n", complete_chain(5));   // 1
    printf("%d\n", complete_chain(-3));  // -1
    printf("%d\n", complete_chain(0));   // 0
    return 0;
}
// Verwachte output:
// [ Warning ] Functie 'incomplete_chain' ...
// 1
// -1
// 0
