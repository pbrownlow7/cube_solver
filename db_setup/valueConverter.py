def convertMultiply():
    f = open("../data/F2LValues.txt", "r")
    m = open("../data/multipliedValues.txt", "w+")
    v = []

    for line in f:
        l = line.split("\n")[0].split("\r")[0].split(", ")
        x = []
        for item in l:
            x.append(int(item))
        #print(x)

        a = x[5]**x[0]
        b = x[1]**x[6]
        c = x[7]**x[2]
        d = x[3]**x[8]
        e = x[9]**x[4]

        val = a + b + c + d + e

        m.write(str(val)+"\n")

        #print(val)

        #v.append(val)
    #print(v)

    f.close()
    m.close()

    dups = 0

    m = open("../data/multipliedValues.txt", "r")

    for line in m:
        l = line.split("\n")[0].split("\r")
        v.append(l)

    for i in range(len(v)):
        for j in range(i+1, len(v)):
            if v[i] == v[j]:
                print("ERROR DUPICATE LINE " + str(i) + " AND " + str(j))
                print(v[i])
                print(v[j])
                dups += 1
                #return

    print(dups)

    #m.close()

def main():
    convertMultiply()

if __name__ == '__main__':
    main()
