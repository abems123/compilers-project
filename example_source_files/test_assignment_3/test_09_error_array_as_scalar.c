// test_09_error_array_as_scalar.c
// Verwacht:
//   [ Error ] Kan niet assignen aan array 'arr': arrays zijn geen lvalues
// Test: array naam direct assignen zonder index

int main() {
    int arr[3];

    // dit is ongeldig: arr is een array, geen scalar variabele
    arr = 5;
}
