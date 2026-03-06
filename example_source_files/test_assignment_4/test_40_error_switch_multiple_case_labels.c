// test_40_error_switch_multiple_case_labels.c
// Verwacht: parse error (syntaxfout)
// Test: meerdere case-labels op één body is NIET ondersteund in onze grammar
// Edge case: in echte C kan je schrijven:
//            case 1:
//            case 2:
//                doe_iets();
//            Maar onze grammar vereist dat elke case zijn eigen body heeft.
//            caseClause : CASE_KW expression COLON statement*
//            Twee case-labels achter elkaar geeft een parse error.

int main() {
    int x = 2;

    switch (x) {
        case 1:
        case 2:
            printf("een of twee\n");
            break;
        default:
            break;
    }
}
