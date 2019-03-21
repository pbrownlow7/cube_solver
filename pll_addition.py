def createKeys():
    f = open("PLLValues.txt", "r")
    f2 = open("PLLKeys.txt", "w+")
    f3 = open("rpiPLLValues.txt", "r")
    f4 = open("rpiPLLKeys.txt", "w+")

    for line in f:
        #alg = f2.readline()
        l = line.split("\n")[0].split("-")
        a = int(l[0][0]) * (int(l[0][1]) + int(l[0][2]))
        b = int(l[1][0]) + (int(l[1][1]) * int(l[1][2]))
        c = (int(l[2][0]) * int(l[2][1])) + int(l[2][2])        
        d = (int(l[3][0]) + int(l[3][1])) * int(l[3][2])
        #for i in range(len(l[0])):
        #    a += int(l[0][i])
        #    b += int(l[1][i])
        #    c += int(l[2][i])
        #    d += int(l[3][i])

        val = (a**c) + (b**d)

        f2.write(str(val) + "\n")

    for line in f3:
        l = line.split("\n")[0].split("-")
        a = int(l[0][0]) * (int(l[0][1]) + int(l[0][2]))
        b = int(l[1][0]) + (int(l[1][1]) * int(l[1][2]))
        c = (int(l[2][0]) * int(l[2][1])) + int(l[2][2])        
        d = (int(l[3][0]) + int(l[3][1])) * int(l[3][2])

        val = (a**c) + (b**d)

        f4.write(str(val) + "\n")

    f.close()
    f2.close()
    f3.close()
    f4.close()

def printKeys():
    f = open("rpiPLLKeys.txt", "r")

    for line in f:
        print(line)

    f.close()

def countLines(): 
    f = open("PLLValues.txt", "r")
    f2 = open("PLLAlgs.txt", "r")

    i = 0
    for line in f:
        i += 1
    print(i)

    i = 0
    for line in f2:
        i += 1
    print(i)

    f.close()
    f2.close()

def main():
    createKeys()
    #countLines()
    printKeys()

if __name__ == '__main__':
    main()
