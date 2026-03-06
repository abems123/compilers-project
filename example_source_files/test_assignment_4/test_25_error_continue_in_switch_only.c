// test_25_error_continue_in_switch_only.c
// Verwacht: [ Error ] 'continue' gebruikt buiten een lus
// Test: continue in een switch body (zonder omringende lus) is ongeldig

int main() {
    int x = 2;

    switch (x) {
        case 1:
            continue;
            break;
        default:
            break;
    }
}
