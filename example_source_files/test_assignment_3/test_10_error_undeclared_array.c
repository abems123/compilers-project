// test_10_error_undeclared_array.c
// Verwacht:
//   [ Error ] gebruik van niet-gedeclareerde array 'ghost'
//   [ Error ] variabele 'x' is geen array en kan niet geïndexeerd worden
// Test: toegang tot niet-gedeclareerde array, en indexeren van scalar

int main() {
    // niet-gedeclareerde array
    int y = ghost[0];

    // scalar als array gebruiken
    int x = 5;
    int z = x[0];
}
