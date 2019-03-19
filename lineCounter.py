def countLines():
    f = open("F2LValues.txt", "r")
    f2 = open("F2LAlgs.txt", "r")
    f3 = open("multipliedValues.txt", "r")

    i = 0
    j = 0
    k = 0

    for line in f:
        i += 1

    for line in f2:
        j += 1

    for line in f3:
        k += 1

    f.close()
    f2.close()
    f3.close()

    print(i)
    print(j)
    print(k)

def main():
    countLines()

if __name__ == '__main__':
    main()
