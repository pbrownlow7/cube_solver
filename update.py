def update():
    allow = ["R", "R'", "L", "L'", "U", "U'", "D", "D'", "F", "F'", "B", "B'", "R2", "L2", "U2", "D2", "F2", "B2"]

    f = open("rpiPLLAlgs.txt", "r")
    i = 0

    for line in f:
        i += 1
        l = line.split("\n")[0].split("\r")[0].split(" ")
        for item in l:
            if item not in allow:
                print(i)
                break

    f.close()

def main():
    update()

if __name__ == '__main__':
    main()
