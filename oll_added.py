def addValues():
    f = open("OLLValues.txt", "r")
    #v = []
    m = open("OLLKeys.txt", "w+")

    for line in f:
        s = line.split("-")
        top = s[0]
        side = s[1].split("\n")[0]
        top_int = bToI(top)
        side_int = bToI(side)
        val = top_int * side_int
        m.write(str(val) + "\n")
        #v.append(val)
        #print(val)
        #print(top)
        #print(side)
        #print(s)
        #print("")
    #testDups(v)

    f.close()
    m.close()

def bToI(bits):
    total = 0
    for i in range(len(bits)):
        total += int(bits[i]) * (2**i)
        #print(bits[i] + "**" + str(i))
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
    #addValues()
    #printKeys()
    #testValues()

if __name__ == '__main__':
    main()
