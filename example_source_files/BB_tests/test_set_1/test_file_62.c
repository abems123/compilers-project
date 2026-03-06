
#define bool int
#define true 1
#define false 0

int main() {
    bool x = true;
    bool y = false;
    bool z = x & y;
    z = z ^ y;
}
