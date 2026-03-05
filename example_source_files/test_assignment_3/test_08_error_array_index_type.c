// test_08_error_array_index_type.c
// Verwacht:
//   [ Error ] array index moet 'int' zijn, maar 'float' gevonden  (arr[1.5])
//   [ Error ] array index mag geen pointer zijn                    (arr[ptr])
//   [ Warning ] array index is van type 'char'                     (arr[c])
// Test: float index, pointer index, char index

int main() {
    int arr[5];

    // float als index → error
    arr[1.5];

    // char als index → warning
    char c = 'A';
    int x = arr[c];

    // pointer als index → error
    int* ptr;
    int y = arr[ptr];
}
