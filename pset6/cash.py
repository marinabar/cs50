while True:
    try:
        change = float(input("Change owed: "))
        if change >= 0 and change <= 100:
            break
    except ValueError:
        print("No.. the input string is not a number. It's a string")

coins = 0
argent = int(round(change * 100))

coins += argent // 25
argent %= 25

coins += argent // 10
argent %= 10

coins += argent // 5
argent %= 5

coins += argent

print(coins)
