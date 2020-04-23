from cs50 import cs50

height = cs50.get_int("Height: ")

while height >= 9 or height <= 0:
    height = cs50.get_int("something went wrong, try again ; height:  ")

if height <= 9 and height >= 0:
    for i in range (0,height):
        print(" " * (height - i - 1), end="")
        print("#" * (1+i), end="")
        print("")
