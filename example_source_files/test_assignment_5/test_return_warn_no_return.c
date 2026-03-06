// test_return_warn_no_return.c
// Verwacht: 2 warnings (missing_return, only_in_if)
// Test: functies zonder return op alle paden

#include <stdio.h>

// FOUT: helemaal geen return
int missing_return(int x) {
    int y = x + 1;
}

// FOUT: alleen return in if, geen else
int only_in_if(int x) {
    if (x > 0) {
        return x;
    }
    // geen return als x <= 0
}

// GOED ter vergelijking: void hoeft geen return
void fine_void(int x) {
    printf("%d\n", x);
}

int main() {
    fine_void(99);  // 99
    return 0;
}
// Verwachte output:
// [ Warning ] Functie 'missing_return' ...
// [ Warning ] Functie 'only_in_if' ...
// 99
