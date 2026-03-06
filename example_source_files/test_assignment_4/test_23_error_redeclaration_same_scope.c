// test_23_error_redeclaration_same_scope.c
// Verwacht: [ Error ] Herhaalde declaratie van variabele 'x'
// Test: dezelfde variabele twee keer declareren in dezelfde scope

int main() {
    int x = 1;
    int x = 2;
}
