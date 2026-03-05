// test_07_error_array_init_length.c
// Verwacht:
//   [ Error ] 'values': verwacht 3 elementen, maar kreeg 2
//   [ Error ] 'other': verwacht 3 elementen, maar kreeg 4
//   [ Error ] 'grid[1]': verwacht 3 elementen, maar kreeg 2
// Test: te weinig, te veel, en verkeerde rij-lengte in 2D

int main() {
    // te weinig elementen
    int values[3] = {1, 2};

    // te veel elementen
    int other[3] = {1, 2, 3, 4};

    // 2D: tweede rij heeft te weinig elementen
    int grid[2][3] = {{1, 2, 3}, {4, 5}};

    // lege initialisator voor non-zero array
    int empty[2] = {};
}
