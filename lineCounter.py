def countLines():
    f = open("F2LValues.txt", "r")
    f2 = open("F2LAlgs.txt", "r")

    i = 0
    j = 0

    for line in f:
        i += 1

    for line in f2:
        j += 1

    f.close()
    f2.close()

    print(i)
    print(j)

def main():
    countLines()

if __name__ == '__main__':
    main()
