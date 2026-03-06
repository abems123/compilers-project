
#ifndef GUARD1
#define GUARD1

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

#endif
