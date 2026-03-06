// test_36_error_vardecl_directly_in_switch.c
// Verwacht: [ Error ] Variabele declaratie direct in switch body zonder anonieme scope
// Test: switch heeft geen eigen scope in C — variabele declaratie direct
//       in een case (zonder { }) is een semantic error in onze compiler
// Edge case: dit is een C-specifieke regel: je moet { } gebruiken om
//            variabelen in een switch te declareren

int main() {
    int x = 2;

    switch (x) {
        case 1:
            int a = 10;
            break;
        case 2:
            printf("%d\n", a);
            break;
    }
}
