import json

def update():
    f = open("../data/oll_stats.txt", "r")
    i = 0
    oll_dict = {}
    for line in f:
        i += 1
        l = line.split("\n")[0]
        if l not in oll_dict.keys():
            oll_dict[l] = 1
        else:
            oll_dict[l] = oll_dict[l]+1
    oll_dict["total"] = i
    #print("Line Total: " + str(i))
    with open("stats.json", "w") as outfile:
        json.dump(oll_dict, outfile)
    f.close()

    f = open("../data/pll_stats.txt", "r")
    i = 0
    pll_dict = {}
    for line in f:
        i += 1
        l = line.split("\n")[0]
	if l not in pll_dict.keys():
            pll_dict[l] = 1
        else:
            pll_dict[l] = pll_dict[l]+1
    pll_dict["total"] = i

    with open("pll_stats.json", "w") as outfile:
	json.dump(pll_dict, outfile)
    f.close()

if __name__ == '__main__':
    update()
