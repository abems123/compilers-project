// test_34_valid_continue_for_goes_to_update.c
// Verwacht: geen errors, geen warnings
// Test: continue in een for-lus — moet naar de update-stap springen,
//       NIET terug naar de conditie. De update (i = i + 1) moet
//       altijd uitgevoerd worden, ook als we continue doen.
// Edge case: in de for→while vertaling staat de update in WhileNode.update,
//            zodat de LLVM visitor weet waar continue naartoe moet springen

#include <stdio.h>

int main() {
    // Met continue: sla i == 3 over, maar i moet wel nog opgehoogd worden
    // Verwacht output: 0 1 2 4  (3 wordt overgeslagen, maar lus gaat verder)
    for (int i = 0; i < 5; i++) {
        if (i == 3) {
            continue;
        }
        printf("%d\n", i);
    }
}
