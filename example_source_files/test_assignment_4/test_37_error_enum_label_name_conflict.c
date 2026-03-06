// test_37_error_enum_label_name_conflict.c
// Verwacht: [ Error ] Herhaalde declaratie — enum label 'status' conflicteert
//           met variabele 'status' in dezelfde scope
// Test: een enum label heeft dezelfde naam als een variabele
// Edge case: enum labels worden als const int in de globale scope geregistreerd,
//            dus een variabele met dezelfde naam is een redeclaratie

enum State {
    ready,
    busy
};

int main() {
    // 'ready' is al een enum label (const int) → redeclaratie!
    int ready = 5;
}
