// test_05_strings_valid.c
// Verwacht: geen errors, geen warnings
// Test: string literals, escape sequences, toewijzen aan char*

#include <stdio.h>

int main() {
    // string toewijzen aan char pointer
    char* s = "hello";

    // string met escape sequences
    char* newline  = "hello\n";
    char* tab      = "hello\t";
    char* backslash = "hello\\";
    char* quote    = "say \"hi\"";

    // lege string
    char* empty = "";

    // string als printf argument
    printf("hello world\n");
    printf("tab:\there\n");

    // string met format codes
    int x = 5;
    printf("x = %d\n", x);
}
