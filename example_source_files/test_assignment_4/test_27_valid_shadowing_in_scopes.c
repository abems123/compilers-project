// test_27_valid_shadowing_in_scopes.c
// Verwacht: geen errors, geen warnings
// Test: dezelfde naam in verschillende scopes is toegestaan (shadowing)

int main() {
    int x = 1;

    {
        int x = 2;
        {
            int x = 3;
        }
    }

    if (x > 0) {
        int x = 10;
    }

    int i = 0;
    while (i < 3) {
        int x = i * 2;
        i = i + 1;
    }
}
