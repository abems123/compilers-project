// test_14_valid_array_with_pointers.c
// Verwacht: geen errors, geen warnings
// Test: arrays gecombineerd met pointers, const, en bestaande features

int main() {
    // pointer naar array element (adres van element)
    int arr[3] = {1, 2, 3};
    int* p = &arr[0];

    // const array (elementen zijn niet const, de declaratie zelf is gewoon)
    int counts[4] = {0, 0, 0, 0};

    // array met negatieve waarden in initialisatie
    int neg[3] = {-1, -2, -3};

    // array element in complexe expressie
    int result = arr[0] * arr[1] + arr[2];

    // array element als argument voor unaire operator
    int val = -arr[1];
    int bit = ~arr[0];
}
