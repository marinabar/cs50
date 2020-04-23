from cs50 import get_string
import sys

# Checks argument number
if len(sys.argv) != 2:
    sys.exit("Usage: ./caesar key")

# Cast key to int
k = int(sys.argv[1])

input = get_string("plaintext: ")
print("ciphertext: ", end='')

# Iterate over plaintext
for r in input:
    # If element is alphabetic
    if r.isalpha:
        # If element is lowercase
        if r.islower:
            k1 = k
            while ord(r) + k1 > ord('z'):
                k1 -= 26
            print(chr (ord(r) + k1), end='')
        # If element is uppercase
        elif r.isupper:
            k2 = k
            while ord(r) + k2 > ord('Z'):
                    k2 -= 26
            print(chr (ord(r) + k2), end='')
    # If element is not alphabetic
    else:
        print(r, end='')
print()
