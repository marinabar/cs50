
from cs50 import get_string
from sys import argv

while True:

    if len(argv) == 2:

        f = open(argv[1], "r")

        break

    else:

        print("Useage: python bleep.py dictionary")

        exit(1)


if f.mode == 'r':

    contents = f.read()

message = input("What message would you like to censor?\n")

words = message.split(" ")

for word in words:

    low_word = word.lower()
    length = len(word)
    if low_word in contents:
        print(length*"*", end=" ")
    else:
        print(word, end=" ")
print()
