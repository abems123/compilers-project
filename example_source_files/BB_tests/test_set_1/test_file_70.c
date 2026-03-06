
#ifndef SOME_GUARD_HH_
#define SOME_GUARD_HH_

// this will be ignored, since the "SOME_GUARD_HH_" symbol is already defined
#include "some_header.h"

#define bool int
#define true 1
#define false 0

int some_func(int x, bool y) {
    if(y) {
        return x*2;
    } else {
        return x << 4;
    }
}

#endif SOME_GUARD_HH_
