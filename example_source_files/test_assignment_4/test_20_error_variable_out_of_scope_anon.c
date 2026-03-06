// test_20_error_variable_out_of_scope_anon.c
// Verwacht: [ Error ] Gebruik van niet-gedeclareerde variabele 'secret'
// Test: variabele gedeclareerd in anonieme scope, gebruikt buiten

int main() {
    {
        int secret = 42;
    }

    int x = secret;
}
