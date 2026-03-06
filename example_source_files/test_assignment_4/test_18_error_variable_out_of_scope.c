// test_18_error_variable_out_of_scope.c
// Verwacht: [ Error ] Gebruik van niet-gedeclareerde variabele 'inner'
// Test: variabele gedeclareerd in if-body, gebruikt buiten if

int main() {
    int x = 5;

    if (x > 0) {
        int inner = 99;
    }

    int y = inner;
}
