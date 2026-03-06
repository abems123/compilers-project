// test_05_valid_anonymous_scope.c
// Verwacht: geen errors, geen warnings
// Test: anonieme scope, variabele shadowing, geneste anonieme scopes

int main() {
    int x = 1;

    // anonieme scope
    {
        int y = 2;
        x = x + y;
    }
    // y is hier niet meer zichtbaar

    // shadowing: binnenste x overschaduwt buitenste x
    {
        int x = 99;
        x = x + 1;
    }
    // buitenste x ongewijzigd

    // geneste anonieme scopes
    {
        int a = 1;
        {
            int b = 2;
            {
                int c = a + b;
            }
        }
    }
}
