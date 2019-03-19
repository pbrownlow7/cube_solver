import redis

def fillDB():
    r = redis.Redis(host='localhost', port=6379, db=0)

    f = open("multipliedValues.txt", "r")
    f2 = open("F2LAlgs.txt")

    for line in f:
        l = line.split("\n")[0].split("\r")[0]
        alg = f2.readline().split("\n")[0].split("\r")[0]

        r.set(l, alg)
        #print(r.get(l))

    f.close()
    f2.close()

def fillOLLDB():
    r = redis.Redis(host='localhost', port=6379, db=1)

    f = open("OLLKeys.txt", "r")
    f2 = open("OLLAlgs.txt", "r")

    #print(r.get('260320'))

    for line in f:
        l = line.split("\n")[0]
        alg = f2.readline().split("\n")[0]
        r.set(l, alg)
    #    print(r.get(l))

    f.close()
    f2.close()

def fillPLLDB():
    r = redis.Redis(host='localhost', port=6379, db=2)

    f = open("PLLKeys.txt", "r")
    f2 = open("PLLAlgs.txt", "r")

    for line in f:
        l = line.split("\n")[0]
        alg = f2.readline().split("\n")[0]
        r.set(l, alg)
        #print(l)
        #print(alg)
        #print("")

    f.close()
    f2.close()

def main():
    fillDB()
    fillOLLDB()
    fillPLLDB()

if __name__ == '__main__':
    main()
