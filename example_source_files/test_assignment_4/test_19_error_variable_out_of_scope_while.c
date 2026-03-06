// test_19_error_variable_out_of_scope_while.c
// Verwacht: [ Error ] Gebruik van niet-gedeclareerde variabele 'tmp'
// Test: variabele gedeclareerd in while-body, gebruikt na de lus

int main() {
    int i = 0;

    while (i < 5) {
        int tmp = i * 2;
        i = i + 1;
    }

    int result = tmp;
}
