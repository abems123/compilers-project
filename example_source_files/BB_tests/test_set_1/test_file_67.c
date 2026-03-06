
#ifndef GUARD2
#define GUARD2

#include "some_header.h"

#define bool int
#define true 1
#define false 0

int adjust_value(int x, bool y) {
    int new_value = some_func(x, y);
    new_value += 6467;

    return new_value;
}

#endif
