// test_01_comments_valid.c
// Verwacht: geen errors, geen warnings
// Test: line comments, block comments, comment op eigen regel, comment na statement

#include <stdio.h>

/* Dit is een
   multi-line
   block comment */

int main() {
    // dit is een line comment op eigen regel
    int x = 5; // comment na statement
    int y = 3; /* inline block comment */

    /* nog een
       multi-line
       comment */

    printf("hello\n"); // comment na printf
}
