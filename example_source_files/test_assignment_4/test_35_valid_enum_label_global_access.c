// test_35_valid_enum_label_global_access.c
// Verwacht: geen errors, geen warnings
// Test: enum labels zijn globaal zichtbaar zonder scope qualifier (C-stijl)
//       Ze zijn beschikbaar overal in main(), ook in geneste scopes
// Edge case: OFFLINE kan gebruikt worden in anonieme scope, while-body,
//            if-body — overal zonder "SYS_IO_ReceiverStatusBit::OFFLINE"

#include <stdio.h>

enum SYS_IO_ReceiverStatusBit {
    READY,
    BUSY,
    OFFLINE
};

int main() {
    // gebruik in anonieme scope
    {
        int x = OFFLINE;
        printf("%d\n", x);
    }

    // gebruik in while-conditie
    int status = BUSY;
    while (status != READY) {
        status = READY;
    }

    // gebruik in if-conditie
    if (status == READY) {
        printf("klaar\n");
    }

    // gebruik in for-lus
    for (int i = READY; i <= OFFLINE; i++) {
        printf("%d\n", i);
    }
}
