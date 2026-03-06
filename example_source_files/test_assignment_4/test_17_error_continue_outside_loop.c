// test_17_error_continue_outside_loop.c
// Verwacht: [ Error ] 'continue' gebruikt buiten een lus
// Test: continue direct in main body

int main() {
    int x = 5;
    continue;
}
