
#include "some_header.h"
#include "some_header2.h"
#include "some_header.h"

#define bool int
#define true 1
#define false 0

int main() {
    int x = some_func(5, true);
    int y = adjust_value(x, false);
}

