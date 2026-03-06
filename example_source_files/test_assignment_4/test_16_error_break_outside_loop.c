// test_16_error_break_outside_loop.c
// Verwacht: [ Error ] 'break' gebruikt buiten een lus of switch statement
// Test: break direct in main body, niet in lus of switch

int main() {
    int x = 5;
    break;
}
