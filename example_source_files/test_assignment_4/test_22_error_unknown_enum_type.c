// test_22_error_unknown_enum_type.c
// Verwacht: [ Error ] Onbekend type 'OnbekendType'
// Test: variabele declareren met een enum type dat niet gedefinieerd is

int main() {
    enum OnbekendType x = 0;
}
