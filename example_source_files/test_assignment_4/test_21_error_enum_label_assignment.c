// test_21_error_enum_label_assignment.c
// Verwacht: [ Error ] Kan niet toewijzen aan const variabele 'RED'
// Test: enum label is const, mag niet geassigned worden

enum Color {
    RED,
    GREEN,
    BLUE
};

int main() {
    RED = 5;
}
