// test_06_error_no_include.c
// Verwacht: [ Error ] gebruik van 'printf' zonder '#include <stdio.h>'
// Verwacht: [ Error ] gebruik van 'scanf' zonder '#include <stdio.h>'
// Test: printf en scanf zonder #include <stdio.h>

int main() {
    printf("hello\n");
    int x;
    scanf("%d", &x);
}
