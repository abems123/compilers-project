// test_39_error_enum_trailing_comma.c
// Verwacht: parse error (syntaxfout)
// Test: trailing comma in enum body is niet toegestaan
// Edge case: enum Foo { A, B, C, }; — de grammar staat dit NIET toe
//            (rule: ID (COMMA ID)* — de laatste COMMA heeft geen ID meer)

enum Foo {
    A,
    B,
    C,
};

int main() {
    int x = A;
}
