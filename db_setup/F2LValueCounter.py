def counter():
    numbers = [["36", "13", "24"], ["38", "22", "33"], ["40", "31", "47"], ["42", "45", "15"]]

    for i in range(len(numbers)):
        f = open("../data/F2LValues.txt", "r")
        total = 0
        for line in f:
            line = line.split("\n")[0].split("\r")[0].split(", ")
            if line[5] == numbers[i][0] and line[6] == numbers[i][1] and line[7] == numbers[i][2]:
                total += 1
        print(total)
        f.close()

def main():
    counter()

if __name__ == '__main__':
    main()
