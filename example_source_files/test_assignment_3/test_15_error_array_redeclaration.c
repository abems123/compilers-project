// test_15_error_array_redeclaration.c
// Verwacht:
//   [ Error ] Herhaalde declaratie van array 'arr'
//   [ Error ] Herhaalde declaratie van variabele 'x' (bestaande check)
// Test: array opnieuw declareren, en ook scalar opnieuw declareren

int main() {
    int arr[3] = {1, 2, 3};
    int arr[5];

    int x = 5;
    int x = 10;
}
