// test_38_error_enum_empty_body.c
// Verwacht: parse error (syntaxfout)
// Test: lege enum body is niet toegestaan door de grammar
// Edge case: enum Foo {}; heeft geen labels → grammar eist minimaal 1 ID

enum Empty {
};

int main() {
    int x = 0;
}
