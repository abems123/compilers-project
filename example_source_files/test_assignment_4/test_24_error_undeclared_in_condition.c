// test_24_error_undeclared_in_condition.c
// Verwacht: [ Error ] Gebruik van niet-gedeclareerde variabele 'onbekend'
// Test: niet-gedeclareerde variabele in if-conditie

int main() {
    if (onbekend > 0) {
        int x = 1;
    }
}
