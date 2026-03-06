// test_01_valid_example_from_assignment.c
// Verwacht: geen errors, geen warnings
// Test: het exacte voorbeeldprogramma uit de opdrachtbeschrijving

#include <stdio.h>

/*
* My program
*/
enum SYS_IO_ReceiverStatusBit {
    READY,
    BUSY,
    OFFLINE
};

int main() {
    enum SYS_IO_ReceiverStatusBit status = BUSY;
    { // unnamed scope
        int x = 1 + 5 + OFFLINE;
        while (x < 10) {
            int result = x * 2;
            if (x > 5) {
                result = result * x;
            }
            printf("%d", result);
            x = x + 1;
        }
    }
}
