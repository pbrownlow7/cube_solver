def addValues():
    f = open("OLLValues.txt", "r")
    f2 = open("rpiOLLValues.txt", "r")
    m = open("OLLKeys.txt", "w+")
    m2 = open("rpiOLLKeys.txt", "w+")
    v1 = []
    v2 = []

    for line in f:
        s = line.split("-")
        top = s[0]
        side = s[1].split("\n")[0]
        top_int = bToI(top)
        side_int = bToI(side)
        val = top_int * side_int
        m.write(str(val) + "\n")
        v1.append(val)

    for line in f2:
        s = line.split("-")
        top = s[0]
        side = s[1].split("\n")[0]
        top_int = bToI(top)
        side_int = bToI(side)
        val = top_int * side_int
        m2.write(str(val) + "\n")
        v2.append(val)

    f.close()
    f2.close()
    m.close()
    m2.close()

    testDups(v1)
    testDups(v2)

def bToI(bits):
    total = 0
    for i in range(len(bits)):
        total += int(bits[i]) * (2**i)
    return total

def testDups(v):
    dups = 0
    for i in range(len(v)):
        for j in range(i+1, len(v)):
            if v[i] == v[j]:
                print("Duplicate: " + str(i) + " " + str(j) + " - " + str(v[i]))
                dups += 1
    print(dups)

def printKeys():
    f = open("OLLKeys.txt", "r")

    for line in f:
        print(line.split("\n")[0])

    f.close()

def testValues():
    f = open("OLLValues.txt", "r")
    f2 = open("OLLAlgs.txt", "r")

    for line in f2:
        print(line),
        l = f.readline()
        print(l)

    f.close()
    f2.close()

def main():
    addValues()
    #printKeys()
    #testValues()

if __name__ == '__main__':
    main()
