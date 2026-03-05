// test_17_error_empty_init.c
// Verwacht:
//   [ Error ] 'arr': verwacht 3 elementen, maar kreeg 0
//   [ Error ] 'grid': verwacht 2 elementen, maar kreeg 0
// Test: lege initialisator voor niet-lege array

int main() {
    // lege 1D initialisator
    int arr[3] = {};

    // lege 2D initialisator
    int grid[2][3] = {};
}
