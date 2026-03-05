// test_12_error_array_init_structure.c
// Verwacht:
//   [ Error ] element 0 van 'grid' moet een rij-initialisator zijn
//   [ Error ] onverwachte geneste initialisator in 1D array 'flat'
// Test: verkeerde nesting structuur in initialisator

int main() {
    // 2D array maar 1D initialisator gegeven
    int grid[2][3] = {1, 2, 3};

    // 1D array maar geneste initialisator gegeven
    int flat[3] = {{1, 2, 3}};
}
