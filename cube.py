import math
import time
import random
import redis

class Graph():

    """
    elems = [left, middle, right]
    ops = [clockwise face, anticlockwise face, clockwise neighbour, anticlockwise neighbour]
    """

    def __init__(self):
        self._elements = {}
        self._index = None

    def addElement(self, index, elems, ops, buddy):
        self._elements[index] = (elems, ops, buddy)
        self._index = index

    def getElements(self, index):
        return self._elements[index][0]

    def getBuddy(self, index):
        return self._elements[index][2]

    def getIndex(self):
        return self._index

    def __str__(self):
        str_desc = ""
        for key in range(len(self._elements.keys())):
            key = str(key)
            str_desc += "%s: (%s)(%s){|%s||%s||%s|}(%s)(%s) Buddy: %s\n" % (key, self._elements[key][1][3], self._elements[key][1][1], \
                                                                          self._elements[key][0][0], self._elements[key][0][1], self._elements[key][0][2], \
                                                                          self._elements[key][1][0], self._elements[key][1][2], self._elements[key][2])
        return str_desc

def buildGraph(f_name):
    g = Graph()
    f = open(f_name, "r")
    for line in f.readlines():
        line = line.split(":")
        index = line[0]
        e = line[1].split(",")
        elems = [int(e[0]), int(e[1]), int(e[2])]
        o = line[2].split(",")
        ops = [o[0], o[1], o[2], o[3]]
        buddy = line[3].strip()
        g.addElement(index, elems, ops, buddy)
    return g

class Cube:

    """
    Cube is the main cube and holds all the functions for representing the cube and manipulating the cube.

    """

    def __init__(self):
        self._graph = buildGraph("config.txt")
        self._middle = buildGraph("middle_config.txt")
        self._opposites = {"R":"O", "W":"Y", "G":"B", "Y":"W", "O":"R", "B":"G"}
        self._translation = {"R":"U", "W":"L", "G":"F", "Y":"R", "O":"D", "B":"B"}
        self._inverts = {"U": "U'", "D": "D'", "L": "L'", "R": "R'", "F": "F'", "B": "B'", "U'": "U", "D'": "D", "L'": "L", "R'": "R", "F'": "F", "B'": "B"}
        self._not_effected = {"R":"L", "L":"R", "U":"D", "D":"U", "F":"B", "B":"F"}
        self._cube = self._createCube()
        self._readable_solution = []
        self._r = redis.Redis(host='localhost', port=6379, db=0)
        self._oll_r = redis.Redis(host='localhost', port=6379, db=1)
        self._pll_r = redis.Redis(host='localhost', port=6379, db=2)

        self._wide_rotations = {"u":('0', 0, '5', 0), "u'":('0', 1, '5', 1), "d":('16', 0, '5', 1), "d'":('16', 1, '5', 0),
                               "l":('3', 2, '0', 0), "l'":('3', 3, '0', 1), "r":('1', 2, '0', 1), "r'":('1', 3, '0', 0),
                               "f":('2', 2, '1', 0), "f'":('2', 3, '1', 1), "b":('0', 2, '1', 1), "b'":('0', 3, '1', 0)}

        self._face_rotations = {"U":('0', 0), "U'":('0', 1), "D":('10', 2), "D'":('10', 3),
                                "L":('3', 2), "L'":('3', 3), "R":('1', 2), "R'":('1', 3),
                                "F":('2', 2), "F'":('2', 3), "B":('0', 2), "B'":('0', 3),
                                "M":('0', 0), "M'":('0', 1)}

        self._cube_rotations = {"x":(0, 0), "x'":(0, 1), "y":(1, 0), "y'":(1, 1), "z":(2, 0), "z'":(2, 1)}

    def _createCube(self):
        cube = []
        c = ["R", "W", "G", "Y", "O", "B"]
        for i in range(54):
            #if i < 9:
            #    s = Square(str(i))
            #else:
            face = faceNumber(i)
            s = Square(c[face])
            #s = Square(str(i))
            cube.append(s)

        return cube

    def Rotate(self, index, op):
        buddyOp = op
        for _ in range(2):
            if buddyOp == 3:
                buddyOp = 0
            else:
                buddyOp += 1
        self._rotate(index, op, self._graph)
        self._rotate(self._graph.getBuddy(index), buddyOp, self._graph)
        self._translateToNotation(index, op)

    def RotateWithNotation(self, letter):
        rotates = 1
        if letter[-1] == "2":
            rotates = 2
            letter = letter[0]

        if letter in self._wide_rotations.keys():
            params = self._wide_rotations[letter]
            for _ in range(rotates):
                self.RotateWide(params[0], params[1], params[2], params[3])
        elif letter in self._cube_rotations.keys():
            params = self._cube_rotations[letter]
            for _ in range(rotates):
                self.RotateCube(params[0], params[1])
        else:
            face = self._face_rotations[letter]
            if letter[0] != "M":
                for _ in range(rotates):
                    self.Rotate(face[0], face[1])
            else:
                for _ in range(rotates):
                    self.RotateMiddle(face[0], face[1])
        #else:
        #    if letter[-1] == "'":
        #        self.RotateMiddle(0, 1)
        #    else:
        #        self.RotateMiddle(0, 0)

    def _rotate(self, index, op, graph):
        elems = []
        next_n = []
        for i in range(4):
            current_elems = graph.getElements(index)
            elems.append([None, [self._cube[current_elems[x]] for x in range(3)]])
            index = graph._elements[index][1][op]
            next_elems = graph.getElements(index)
            elems[i][0] = next_elems
            if i == 3:
                for j in range(1, 5):
                    for k in range(3):
                        self._cube[elems[j*-1][0][k]] = elems[j*-1][1][k]

    def RotateMiddle(self, index, op):
        self._rotate(index, op, self._middle)

    def RotateWide(self, index, op, mid_index, mid_op):
        self.Rotate(index, op)
        self.RotateMiddle(mid_index, mid_op)

    def RotateCube(self, index, op):
        """
        index ==> 0:x, 1:y, 2:z
        op ==> 0:clockwise, 1:anticlockwise
        """
        if index == 0:
            if op == 0:
                wide = self._wide_rotations["l'"]
                face = self._face_rotations["R"]
            else:
                wide = self._wide_rotations["l"]
                face = self._face_rotations["R'"]
        elif index == 1:
            if op == 0:
                wide = self._wide_rotations["u"]
                face = self._face_rotations["D'"]
            else:
                wide = self._wide_rotations["u'"]
                face = self._face_rotations["D"]
        else:
            if op == 0:
                wide = self._wide_rotations["f"]
                face = self._face_rotations["B'"]
            else:
                wide = self._wide_rotations["f'"]
                face = self._face_rotations["B"]
        self.RotateWide(wide[0], wide[1], wide[2], wide[3])
        self.Rotate(face[0], face[1])

    def printNodes(self):
        for index in range(24):
            index = str(index)
            elems = self._graph.getElements(index)
            print("|%s||%s||%s|" % (self._cube[elems[0]].colour, self._cube[elems[1]].colour, self._cube[elems[2]].colour))

    def _representCube(self):
        str_desc = ""
        i = 0
        while i < 54:
            str_desc += "|%s||%s||%s|\n|%s||%s||%s|\n|%s||%s||%s|\n---------\n" % (self._cube[i].colour, self._cube[i+1].colour, self._cube[i+2].colour, self._cube[i+7].colour, self._cube[i+8].colour, self._cube[i+3].colour, self._cube[i+6].colour, self._cube[i+5].colour, self._cube[i+4].colour)
            i += 9
        return str_desc

    def SolveCross(self):
        correct_states = []
        in_position = []
        targets = self._searchForCross(in_position)
        targets = self._checkCross(targets, in_position)
        positions = targets[0]
        buddies = targets[1]
        state_index = targets[2]
        moves = dict()
        for i in range(len(positions)):
            m = self._findClosestSquare(positions[i], state_index)
            moves[m[0]] = m[1]
        sorted_distances = self._sortDistances(moves)
        correct_states = self._crossMove(sorted_distances[0], moves[sorted_distances[0]], correct_states, state_index)
        in_position.append(buddies[sorted_distances[0]])
        #print(correct_states)

        while len(correct_states) < 4:
            targets = self._searchForCross(in_position)
            positions = targets[0]
            buddies = targets[1]
            state_index = targets[2]
            target_positions = [self._findTarget(positions[i], correct_states[0]) for i in range(len(positions))]
            moves = dict()
            for i in range(len(positions)):
                m = self._findClosestSquare(positions[i], state_index)
                moves[m[0]] = m[1]
            sorted_distances = self._sortDistances(moves)
            correct_states = self._crossMove(sorted_distances[0], moves[sorted_distances[0]], correct_states, state_index)
            in_position.append(buddies[sorted_distances[0]])
        self._checkCrossOrientation(correct_states[0])
        #self._cleanUpSolution()
        return self._cleanUpSolution(self._readable_solution)

    def _checkCross(self, targets, in_position):
        count = 0
        culprits = []
        for i in range(len(targets[0])):
            m = self._findClosestSquare(targets[0][i], targets[2])
            if len(m[1]) == 0:
                culprits.append(m[0])
                count += 1
        if count > 1:
            worst = self._rankCulprits(culprits)
            if worst[1][worst[0]] > 0:
                return targets
            self.Rotate(worst[0], 2)
            targets = self._searchForCross(in_position)
            return self._checkCross(targets, in_position)
        return targets

    def _rankCulprits(self, culprits):
        rankings = dict()
        for c in culprits:
            rankings[c] = 0

        for c in culprits:
            for c2 in culprits:
                if c != c2:
                    state = self._findTarget(c2, c)
                    if c2 == state:
                        rankings[c2] += 1
        worst = None
        for key in rankings.keys():
            if worst == None or rankings[key] < worst:
                worst = key
        return (worst, rankings)

    def _checkCrossOrientation(self, inserted):
        inserted_buddy = self._graph.getBuddy(inserted)
        new_state = inserted
        inserted_turns = 0
        for i in range(1, 4):
            new_state = self._graph._elements[new_state][1][0]
            target_state = self._graph.getBuddy(new_state)
            center = ((self._graph.getElements(target_state)[1] / 9) * 9) + 8
            if self._cube[self._graph._elements[inserted_buddy][0][1]].colour == self._cube[center].colour:
                inserted_turns = i

        for _ in range(inserted_turns):
            self.Rotate(inserted, 0)

    def _crossMove(self, index, path, correct_states, state_index):
        for i in range(len(path)):
            prev = index
            index = self._graph._elements[prev][1][path[i]]
            if len(correct_states) > 0:
                if int(index) >= state_index and int(index) <= state_index+3:
                    while self._findTarget(prev, correct_states[0]) != index:
                        for x in range(len(correct_states)):
                            correct_states[x] = self._graph._elements[correct_states[x]][1][0]
                        self.Rotate(index, 0)
                    self.Rotate(prev, path[i])
                else:
                    while self._collides(index, correct_states, path[i]):
                        self.Rotate(correct_states[0], 0)
                        for x in range(len(correct_states)):
                            correct_states[x] = self._graph._elements[correct_states[x]][1][0]
                    self.Rotate(prev, path[i])
            else:
                self.Rotate(prev, path[i])
        correct_states.append(index)
        return correct_states

    def _searchForCross(self, in_position):
        center_position = self._findCenter("O")
        positions = []
        target_positions = []
        buddies = dict()
        index = 0
        found = 0
        while found < 4:
            i = str(index)
            if self._cube[self._graph.getElements(i)[1]].colour == "O":
                #print(i)
                #print(self._graph.getElements(i))
                #print(self._cube[int(i)].colour)
                found += 1
                buddy = self._cube[self._graph.getElements(self._graph.getBuddy(i))[1]].colour
                if buddy not in in_position:
                    positions.append(i)
                    buddies[i] = buddy
            index += 1
        #print(self)
        #print(positions)
        #buddies = [self._cube[self._graph.getElements(self._graph.getBuddy(i))[1]].colour for i in positions]
        #buddies = dict()
        #for i in positions:
        #    buddies[i] = self._cube[self._graph.getElements(self._graph.getBuddy(i))[1]].colour
        state_index = (center_position / 9) * 4
        return (positions, buddies, state_index)

    def _findTarget(self, index, inserted):
        inserted_buddy = self._graph.getBuddy(inserted)
        index_buddy = self._graph.getBuddy(index)
        new_state = inserted
        inserted_turns = 0
        index_turns = 0
        for i in range(1, 5):
            new_state = self._graph._elements[new_state][1][0]
            target_state = self._graph.getBuddy(new_state)
            center = ((self._graph.getElements(target_state)[1] / 9) * 9) + 8
            if self._cube[self._graph._elements[inserted_buddy][0][1]].colour == self._cube[center].colour:
                index_state = new_state
                for j in range(1, 5):
                    index_state = self._graph._elements[index_state][1][0]
                    t_state = self._graph.getBuddy(index_state)
                    c = ((self._graph.getElements(t_state)[1] / 9) * 9) + 8
                    if self._cube[self._graph._elements[index_buddy][0][1]].colour == self._cube[c].colour:
                        index_turns = j
                        break
                break
        new_state = inserted
        for _ in range(index_turns):
            new_state = self._graph._elements[new_state][1][0]
        return new_state

    def _findClosestSquare(self, current, state_index):
        #print(self._graph.getElements(str(current))[1])
        #print(self._graph.getElements(str(state_index))[1])
        open_set = Queue()
        closed_set = []
        meta = dict()

        root = current
        meta[root] = None
        open_set.enqueue(root)

        while not open_set.empty():
            subtree_root = open_set.dequeue()
            if int(subtree_root) >= state_index and int(subtree_root) <= state_index+3:
                return self._constructPath(subtree_root, meta)

            for node in self._graph._elements[str(subtree_root)][1]:
                if node in closed_set:
                    continue

                if node not in open_set:
                    meta[node] = subtree_root
                    open_set.enqueue(node)

            closed_set.append(subtree_root)

    def _findPath(self, current, target, correct_states):
        #print(target)
        open_set = Queue()
        closed_set = []
        meta = dict()

        root = current
        meta[root] = None
        open_set.enqueue(root)

        while not open_set.empty():
            subtree_root = open_set.dequeue()
            #print(subtree_root)
            if subtree_root == target:
                return self._constructPath(subtree_root, meta)

            for node in self._graph._elements[subtree_root][1]:
                states = []
                min_state = str((self._graph.getElements(target)[1] / 9) * 4)
                for i in range(3):
                    if min_state != target:
                        states.append(min_state)
                    min_state = self._graph._elements[str(min_state)][1][0]
                #print(states)
                #print(node)
                #print(node in states)
                #coll = self._collides(node, correct_states)

                if node in closed_set:# or self._collides(node, correct_states):# or node in states:
                    #print(node)
                    continue

                if node not in open_set:
                    meta[node] = subtree_root
                    open_set.enqueue(node)

            closed_set.append(subtree_root)

    def _collides(self, node, correct_states, op):
        buddy = self._graph.getBuddy(node)
        for _ in range(4):
            if node in correct_states or buddy in correct_states:
                return True
            node = self._graph._elements[node][1][op]
            buddy = self._graph.getBuddy(node)
        return False
        #if self._cube[self._graph._elements[correct_states[0]][0][1]].colour != "O":
        #    #print(self._cube[self._graph._elements[correct_states[0]][0][1]].colour)
        #    return True
        #buddy = self._graph.getBuddy(node)
        #if node in correct_states:
        #    return True
        #return False

    def _constructPath(self, subtree, meta):
        path = [subtree]
        while meta[subtree] != None:
            path = [meta[subtree]] + path
            subtree = meta[subtree]
        for i in range(1, len(path)):
            i = i*-1
            index = path[i]
            for j in range(len(self._graph._elements[path[i-1]][1])):
                if self._graph._elements[path[i-1]][1][j] == index:
                    path[i] = j
        del path[0]
        return (subtree, path)

    def _distance(self, index, moves):
        return (index, len(moves))

    def _sortDistances(self, moves):
        distances = [(key, moves[key]) for key in moves.keys()]
        sorted_distances = []
        while len(distances) > 0:
            low = 0
            other = 1
            while other < len(distances):
                if len(distances[other][1]) < len(distances[low][1]):
                    low = other
                other += 1
            sorted_distances.append(distances[low][0])
            del distances[low]
        return sorted_distances

    #Start of F2L
    def SolveF2L(self):
        for i in range(4):
            print("")
            print("F2L PAIR " + str(i+1) + ":")
            self._searchForF2L()

    def _searchForF2L(self):
        cross_colour = "O"
        slot_deciders = [(14, 23), (23, 32), (32, 46), (46, 14)]
        slots = [(36, 13, 24, 12, 25), (38, 22, 33, 21, 34), (40, 31, 47, 30, 48), (42, 45, 15, 52, 16)]
        """corner_positions = {0:[51, 9], 2:[49, 39], 6:[11, 18], 4:[20, 27], \
                            9:[0, 51], 11:[6, 18], 15:[42, 45], 13:[24, 36], \
                            18:[6, 11], 20:[4, 27], 24:[13, 36], 22:[33, 38], 27:[4, 20],\
                            29:[2, 49], 33:[22, 38], 31:[40, 47], 36:[24, 13], 38:[22, 33],\
                            42:[15, 45], 40:[31, 47], 45:[15, 42], 47:[40, 31], 51:[0, 9], 49:[2, 29]}
        side_positions = {1:50, 3:28, 5:19, 7:10, 10:7, 12:25, 16:52, 19:5, 21:34, \
                          25:12, 28:3, 30:48, 34:21, 50:1, 52:16, 48:30}"""

        corner_positions = {0:[9, 51], 9:[51, 0], 51:[0, 9], 2:[49, 29], 49:[29, 2], 29:[2, 49], \
                            4:[27, 20], 27:[20, 4], 20:[4, 27], 6:[18, 11], 18:[11, 6], 11:[6, 18], \
                            13:[24, 36], 24:[36, 13], 36:[13, 24], 45:[15, 42], 15:[42, 45], 42:[45, 15], \
                            31:[47, 40], 47:[40, 31], 40:[31, 47], 22:[33, 38], 33:[38, 22], 38:[22, 33]}

        side_positions = {1:50, 3:28, 5:19, 7:10, 10:7, 12:25, 16:52, 19:5, 21:34, \
                          25:12, 28:3, 30:48, 34:21, 50:1, 52:16, 48:30}

        #f2l_pairs = [None, None, None, None]
        
        found = 0
        corner = [0, 0, 0]
        side= [0, 0]
        pair = []
        #corners = [[None, None, None], [None, None, None], [None, None, None], \
        #           [None, None, None]]

        #sides = [[None, None], [None, None], [None, None], [None, None]]
        
        for k in corner_positions.keys():
            if self._cube[k].colour == cross_colour:
                corner[0] = k
                corner[1] = (self._cube[corner_positions[k][0]].colour, corner_positions[k][0])
                corner[2] = (self._cube[corner_positions[k][1]].colour, corner_positions[k][1])

                """corners[found][0] = k
                c1_position = corner_positions[k][0]
                c1_colour = self._cube[c1_position].colour
                corners[found][1] = (c1_colour, c1_position)

                c2_position = corner_positions[k][1]
                c2_colour = self._cube[c2_position].colour
                corners[found][2] = (c2_colour, c2_position)"""

                for sk in side_positions.keys():
                    s2_position = side_positions[sk]
                    s2_colour = self._cube[s2_position].colour
                    
                    if self._cube[sk].colour == corner[1][0] and s2_colour == corner[2][0]:
                        s1_position = sk
                        s1_colour = self._cube[sk].colour
                        side[0] = (s1_colour, s1_position)
                        side[1] = (s2_colour, s2_position)

                        break

                pair = [corner[0], corner[1], corner[2], side[0], side[1], 0, 0, 0, 0, 0]

                """for sk in side_positions.keys():
                    s2_position = side_positions[sk]
                    s2_colour = self._cube[s2_position].colour
                    
                    if self._cube[sk].colour == c1_colour and s2_colour == c2_colour:
                        s1_position = sk
                        s1_colour = self._cube[sk].colour
                        sides[found][0] = (s1_colour, s1_position)

                        sides[found][1] = (s2_colour, s2_position)
                        break"""
                

                s = 0
                c1 = None
                c2 = None
                s1 = None
                s2 = None
                while s < len(slot_deciders):
                    if pair[1][0] == self._cube[slot_deciders[s][0]].colour and pair[2][0] == self._cube[slot_deciders[s][1]].colour:
                        c1 = slots[s][1]
                        c2 = slots[s][2]
                        s1 = slots[s][3]
                        s2 = slots[s][4]
                        break
                    elif pair[1][0] == self._cube[slot_deciders[s][1]].colour and pair[2][0] == self._cube[slot_deciders[s][0]].colour:
                        c1 = slots[s][2]
                        c2 = slots[s][1]
                        s1 = slots[s][4]
                        s2 = slots[s][3]
                        break
                    s += 1

                pair[5] = slots[s][0]
                pair[6] = c1
                pair[7] = c2
                pair[8] = s1
                pair[9] = s2
                
                #print(pair)
                total = abs(pair[0] - pair[5]) + abs(pair[1][1] - pair[6]) + abs(pair[2][1] - pair[7]) + abs(pair[3][1] - pair[8]) + abs(pair[4][1] - pair[9])
                
                if total == 0:
                    #found += 1
                    continue
                else:
                    self._calculatePair(pair)
                    break

                #if found == 4:
                #    break

        """s = 0
        c1 = None
        c2 = None
        s1 = None
        s2 = None
        while s < len(slot_deciders):
            if f2l_pairs[0][0][1][0] == self._cube[slot_deciders[s][0]].colour and f2l_pairs[0][0][2][0] == self._cube[slot_deciders[s][1]].colour:
                c1 = slots[s][1]
                c2 = slots[s][2]
                s1 = slots[s][3]
                s2 = slots[s][4]
                break
            elif f2l_pairs[0][0][1][0] == self._cube[slot_deciders[s][1]].colour and f2l_pairs[0][0][2][0] == self._cube[slot_deciders[s][0]].colour:
                c1 = slots[s][2]
                c2 = slots[s][1]
                s1 = slots[s][4]
                s2 = slots[s][3]
                break
            s += 1
        print(f2l_pairs[0])
        print(c1, c2, s1, s2)

        pair = [f2l_pairs[0][0][0], f2l_pairs[0][0][1][1], f2l_pairs[0][0][2][1], f2l_pairs[0][1][0][1], f2l_pairs[0][1][1][1], slots[s][0], c1, c2, s1, s2]
        self._calculatePair(pair)"""

    def _calculatePair(self, pair):
        a = pair[5]**pair[0]
        b = pair[1][1]**pair[6]
        c = pair[7]**pair[2][1]
        d = pair[3][1]**pair[8]
        e = pair[9]**pair[4][1]
        val = a + b + c + d + e
        #print(pair)
        alg = self._r.get(val)
        #print("")
        print(alg)
        a = alg.split(" ")
        for r in a:
            self.RotateWithNotation(r)

    def SolveOLL(self):
        self._solveOLL()

    def _solveOLL(self):
        cross_colour = "O"
        top_squares = [0, 1, 2, 7, 8, 3, 6, 5, 4]
        side_squares = [51, 50, 49, 29, 28, 27, 20, 19, 18, 11, 10, 9]
        match_colour = self._opposites[cross_colour]
        turns = []
        alg = None

        while True:
            top_bits = []
            side_bits = []

            for i in top_squares:
                if self._cube[i].colour == match_colour:
                    top_bits.append(1)
                else:
                    top_bits.append(0)

            for i in side_squares:
                if self._cube[i].colour == match_colour:
                    side_bits.append(1)
                else:
                    side_bits.append(0)
            
            #print(top_bits)
            #print(side_bits)
            top_val = self._bToI(top_bits)
            side_val = self._bToI(side_bits)
            alg_value = top_val * side_val
            alg = self._oll_r.get(str(alg_value))
            if alg != None:
                break
            else:
                turns.append("U")
                self.RotateWithNotation("U")
            #print(top_bits)
            #print(side_bits)
        #print(turns)
        if len(turns) > 0:
            print("")
            print("ALLIGNMENT:")
            if len(turns) == 3:
                print(turns[0] + "'")
            elif len(turns) == 2:
                print(turns[0] + "2")
            else:
                print(turns[0])

        print("")
        print("OLL:")
        print(alg)
        a = alg.split(" ")
        for i in a:
        #    print(i)
            self.RotateWithNotation(i)
            #print(alg_value)

    def _bToI(self, bits):
        total = 0
        for bit in range(len(bits)):
            total += bits[bit] * (2**bit)
        return total

    def SolvePLL(self):
        self._solvePLL()

    def _solvePLL(self):
        pll_skip = False
        if (self._cube[51].colour == self._cube[50].colour and self._cube[50].colour == self._cube[49].colour) and \
            (self._cube[29].colour == self._cube[28].colour and self._cube[28].colour == self._cube[27].colour):
            self._alignAfterPLL()
            pll_skip = True
        alg = None
        turns = []
        #col_to_num = {self._cube[17].colour:1, self._cube[26].colour:2, self._cube[35].colour:3, self._cube[53].colour:4}
        side_positions = [51, 50, 49, 29, 28, 27, 20, 19, 18, 11, 10, 9]

        while alg == None and not pll_skip:
            l = [[], [], [], []]
            cols = {}
            for i in range(len(side_positions)):
                colour = self._cube[side_positions[i]].colour
                if colour not in cols.keys():
                    cols[colour] = len(cols)+1
                l[i/3].append(cols[colour])
                #col = self._cube[side_positions[i][j]].colour
                #l[i].append(col_to_num[col])



            a = l[0][0] * (l[0][1] + l[0][2])
            b = l[1][0] + (l[1][1] * l[1][2])
            c = (l[2][0] * l[2][1]) + l[2][2]
            d = (l[3][0] + l[3][1]) * l[3][2]

            val = a**c + b**d
            alg = self._pll_r.get(str(val))
            #print(val)
            #print(alg)
            
            #print(l)
            if alg == None:
                turns.append("U")
                self.RotateWithNotation("U")
            #if len(turns) == 4:
            #    return
        
        if not pll_skip:
            if len(turns) > 0:
                print("")
                print("ALLIGNMENT:")
                if len(turns) == 3:
                    print(turns[0] + "'")
                elif len(turns) == 2:
                    print(turns[0] + "2")
                else:
                    print(turns[0])

            print("")
            print("PLL:")
            print(alg)
            a = alg.split(" ")
            for i in a:
                self.RotateWithNotation(i)
            self._alignAfterPLL()

    def _alignAfterPLL(self):
        turns = []
        while self._cube[51].colour != self._cube[52].colour:
            self.RotateWithNotation("U")
            turns.append("U")

        if len(turns) > 0:
            print("")
            print("ALLIGNMENT:")
            if len(turns) == 3:
                print(turns[0] + "'")
            elif len(turns) == 2:
                print(turns[0] + "2")
            else:
                print(turns[0])

    def _returnCornerBuddies(self, state, position):
        buddies = []
        buddy_position = 0
        if position == 0:
            buddy_position = 2
        buddies.append(self._cube[self._graph._elements[self._graph.getBuddy(state)][0][buddy_position]].colour)
        if position == 0:
            state = self._graph._elements[str(state)][1][1]
        else:
            state = self._graph._elements[str(state)][1][0]
        buddies.append(self._cube[self._graph._elements[self._graph.getBuddy(state)][0][position]].colour)
        return (buddies[0], buddies[1])

    def _findCenter(self, colour):
        for index in range(12):
            index = str(index)
            if self._cube[self._middle.getElements(index)[1]].colour == colour:
                return self._middle.getElements(index)[1]

    def _translateToNotation(self, state, op):
        t = ""
        if op < 2:
            key = self._cube[((int(state)/4) * 9) + 8].colour
        else:
            buddy = self._graph.getBuddy(state)
            key = self._cube[((int(buddy)/4) * 9) + 8].colour
        t += self._translation[key]

        if op % 2 != 0:
            t += "'"
        self._readable_solution.append(t)

    def _cleanUpSolution(self, solution):
        new_solution = []
        null = []

        for i in range(len(solution)):
            if i in null:
                continue
            elif i == len(solution)-1:
                new_solution.append(solution[i])

            for j in range(i+1, len(solution)):
                if solution[j][0] == self._not_effected[solution[i][0]]:
                    continue
                elif solution[j] == solution[i]:
                    new_solution.append(solution[i][0]+"2")
                    null.append(j)
                    break
                else:
                    new_solution.append(solution[i])
                    break

        """for move in solution:
            #i = random.randint(0, 11)
            #m = moves[i]

            if len(new_solution) == 0:
                new_solution.append(move)
            else:
                if new_solution[len(new_solution)-1] == self._inverts[move]:# or new_solution[len(new_solution)-1] == (move[:1]+"2"):
                    continue

                if new_solution[len(new_solution)-1] == (move+"2"):
                    new_solution[len(new_solution)-1] = new_solution[len(new_solution)-1][:1]+"'"

                elif new_solution[len(new_solution)-1] == move:
                    new_solution[len(new_solution)-1] = new_solution[len(new_solution)-1][:1]+"2"
                else:
                    new_solution.append(move)"""
        #print(solution)
        #print(new_solution)
        return new_solution
            
    def __str__(self):
        return self._representCube()

class Face:
    
    """
    Face represents the faces of the cube - 6 in total.
    Colour is the colour of the face (based on the center square) and is an int.
    Neighbours are the positions of the neighbours of the face
    Square_positions is to make turning the face easier (Rethink this - can do it better probably)
    """

    def __init__(self, colour, opposite, neighbours):
        self._colour = colour
        self._opposite = opposite
        self._neighbours = neighbours

class Square:

    """
    Square represents the individual squares of each face
    """

    def __init__(self, colour):
        self._colour = colour

    def getColour(self):
        return self._colour

    colour = property(getColour)

class Queue:

    def __init__(self):
        self._q = []

    def enqueue(self, item):
        self._q.append(item)

    def dequeue(self):
        item = self._q[0]
        del self._q[0]
        return item

    def empty(self):
        if len(self._q) == 0:
            return True
        return False

    def __contains__(self, item):
        for i in self._q:
            if item == i:
                return True
        return False

def listPosition(face, face_position):
    return (9 * face) + face_position

def faceNumber(list_position):
    return int(list_position / 9)

def facePosition(list_position):
    return list_position - (9 * faceNumber(list_position))

def neighbourNumber(face_position):
    return face_position / 2

def targetSpace(face, list_position):
    return (9 * face) + facePosition(list_position)

def increaseIndexByTwo(index, direction):
    t = index + (2 * direction)
    if t < 0 or t > 7:
        return index + (6 * (direction * -1))
    else:
        return t

def increaseIndexByOne(index, direction):
    t = index + (1 * direction)
    if t < 0 or t > 7:
        return index + (7 * (direction * -1))
    else:
        return t

def main():

    #CheckAlgCorrectness()
    #CheckOLLAlgs()
    #CheckPLLAlgs()

    #c = Cube()
    #print(c)
   
    #total = 0
    #for _ in range(1000):
    
    c = CreateScramble()
    #print(c)
    
    print("")
    print("SOLUTION:")
    start = time.time()
    solve = c.SolveCross()
    nice_solve = "" + solve[0]
    for i in range(1, len(solve)):
        nice_solve += " " + solve[i]
    print("CROSS:")
    print(nice_solve)
    c.SolveF2L()
    c.SolveOLL()
    c.SolvePLL()
    fin = time.time()
    print("")
    print("Total time for solve: " + str(fin-start) + " seconds")
    
    #print(c)
    #    total += fin-start
    #    print("")
    #print("Average over 1000 scrambles: " + str(total/1000))
    #print("")
    #print(c)

    #total_time = 0
    #correct = 0
    #total = 100000
    #for _ in range(total):
    
    #c = TestScramble()
    #    start = time.time()
    
    #    finish = time.time()
    #    total_time += finish-start
        #if DetermineCorrectness(c):
        #    correct += 1
    #print("Average time of %s: %.5f\nCorrect cross solves: %d/%s" % (total, total_time/100, correct, total))
    #print(start)
    #print(finish)
    #print("Solve for cross found in %.10f seconds" % (finish-start))
    
    #print(c._returnCornerBuddies('11', 2))

    #c = EnterScramble()
    #start = time.time()
    #solve = c.SolveCross()
    #finish= time.time()
    #print("Solve for cross found in %.4f seconds" % (finish-start))
    #print(solve)
    
    #c = TestScramble()
    #print(c)
    #print(c._findCenter("O"))
    #StressTestSearchForCross()
    #c.SolveCross()
    #print(c)
    
    #print(c)
    #start = time.time()
    #TestFullSexyRotation(c)
    #end = time.time()
    #print(c)
    #print(end-start)

    #StressTestCubeRotation()
    #TestFullSexyRotation(c)
    #c.Rotate('0', 1)
    #c.Rotate('0', 0)
    #c.Rotate('0', 0)
    #c.Rotate('0', 0)
    #print(c)

    #StressTestCubeRotation()

    #c = Cube()
    #print(c)
    #c.RotateCube(-1, 2)
    #print(c)
    #TestFullSexyRotation(c)
    #for _ in range(4):
    #    c._rotateWide(1, 1)
    #    print(c)
    #c._rotateLayer(1, 0)
    #print(c._cube[36].colour)
    #TestLayerRotation(1, 5)
    
    """c = Cube()
    print(c._cube)
    print("")
    print("")
    for k in c._faces.keys():
        print("%s : %s" % (c._faces[k]._colour, c._faces[k]._opposite))"""

    """TestFaceRotationClockwise()"""

    """TestFaceRotationAntiClockwise()"""

    """TestNeighbourRotationClockwise()"""

    """TestNeighbourRotationAntiClockwise()"""

    #TestFullSexyRotation()

    #TestCenterRotationClockwise()

    """TestCenterRotationAntiClockwise()"""

    """c = TestMixtureOfFullAndCenterRotations()
    RetestMixturceOfFullAndCenterRotaions(c)"""

    """TestBigRotationRightClockwise()"""

    """TestBigRotationRightAntiClockwise()"""

    #TestBigRotationLeftClockwise()

def DetermineCorrectness(c):
    state = "16"
    for _ in range(4):
        buddy = c._graph.getBuddy(state)
        center = c._cube[((c._graph._elements[buddy][0][1]/9)*9)+8].colour
        if c._cube[c._graph._elements[buddy][0][1]].colour != center or c._cube[c._graph._elements[state][0][1]].colour != "O":
            return False
    return True

def StressTestSearchForCross():
    c = Cube()
    start = time.time()
    for _ in range(10000):
        c._searchForCross()
    finish = time.time()
    print(finish-start)

def StressTestFaceRotation():
    c = Cube()
    start = time.time()
    for _ in range(100000):
        c.Rotate('0', 0)
    finish = time.time()
    print(finish-start)

def StressTestMiddleRotation():
    c = Cube()
    start = time.time()
    for _ in range(100000):
        c.RotateMiddle('0', 0)
    finish = time.time()
    print(finish-start)

def StressTestWideRotation():
    c = Cube()
    start = time.time()
    for _ in range(100000):
        c.RotateWide('0', 0, '5', 0)
    finish = time.time()
    print(finish-start)

def StressTestCubeRotation():
    c = Cube()
    start = time.time()
    for _ in range(100000):
        c.RotateCube(0, 0)
    finish = time.time()
    print(finish-start)

def TestBigRotationLeftClockwise():
    c = Cube()
    print(c)
    for _ in range(4):
        c.RotateBig(1, 1)
        print(c)

def TestBigRotationRightClockwise():
    c = Cube()
    print(c)
    for _ in range(4):
        c.RotateBig(1, 3)
        print(c)

def TestBigRotationRightAntiClockwise():
    c = Cube()
    print(c)
    for _ in range(4):
        c.RotateBig(-1, 3)
        print(c)

def TestMixtureOfFullAndCenterRotations():
    c = Cube()
    print(c)
    c.RotateFace(1, 3)
    print(c)
    c.RotateFace(-1, 4)
    print(c)
    c.RotateCenter(1)
    print(c)
    c.RotateFace(1, 0)
    print(c)
    c.RotateCenter(-1)
    print(c)
    c.RotateFace(1, 2)
    print(c)
    return c

def RetestMixturceOfFullAndCenterRotaions(c):
    c.RotateFace(-1, 2)
    c.RotateCenter(1)
    c.RotateFace(-1, 0)
    c.RotateCenter(-1)
    c.RotateFace(1, 4)
    c.RotateFace(-1, 3)
    print(c)

def TestCenterRotationClockwise():
    c = Cube()
    print(c)
    for _ in range(4):
        c.RotateCenter(1, 1)
        print(c)

def TestCenterRotationAntiClockwise():
    c = Cube()
    print(c)
    for _ in range(4):
        c.RotateCenter(-1, 0)
        print(c)

def TestFaceRotationClockwise():
    c = Cube()
    print(c)
    for _ in range(4):
        c._turnFace(1, 0)
        print(c)

def TestFaceRotationAntiClockwise():
    c = Cube()
    print(c)
    for _ in range(4):
        c._turnFace(-1, 0)
        print(c)

def TestNeighbourRotationClockwise():
    c = Cube()
    print(c)
    for _ in range(4):
        c._turnNeighbours(1, 0)
        print(c)

def TestNeighbourRotationAntiClockwise():
    c = Cube()
    print(c)
    for _ in range(4):
        c._turnNeighbours(-1, 0)
        print(c)

def TestFullFaceAndNeighbourRotation():
    c = Cube()
    print(c)
    for _ in range(4):
        c.RotateFace(1, 0)
        print(c)

def TestFullSexyRotation(c):
    for _ in range(6):
        c.RotateWithNotation("R")
        c.RotateWithNotation("U")
        c.RotateWithNotation("R'")
        c.RotateWithNotation("U'")
        #print(c)
    """for _ in range(6):
        c.Rotate('1', 2)
        c.Rotate('0', 0)
        c.Rotate('1', 3)
        c.Rotate('0', 1)
        #print(c)"""

def TestScramble():
    c = Cube()
    #s = ["D", "D", "U", "U", "R'", "B", "B", "L'", "F", "D'", "F", "F", "L", "L", "B'", "R", "R", "U'", "R", "U'", "R", "R", "D'", "R", "L", "L", "B'", "F", "F"]
    #s = ["D", "D", "L", "B", "B", "F", "F", "R", "F", "F", "D", "D", "L'", "B", "B", "L'", "U", "R'", "B'", "U", "U", "L", "B'", "D'", "R", "D", "D", "U'"]
    #s = ["B", "U'", "L'", "B", "L", "F'", "U'", "D", "D", "L", "F", "R'", "D", "D", "F", "R", "R", "F", "F", "R", "R", "L", "L", "F'", "R", "R"]
    #s = ["R", "U", "R'", "L", "U'", "D", "D", "L", "L", "U'", "F", "F"]
    s = ["R", "R", "U", "F", "F", "U'", "R", "R", "L", "U'", "D", "D", "L", "L", "U'", "F", "F", "D", "R'"]
    #s = ["B", "U'", "L'", "B", "L", "F'", "U'", "D", "D", "L", "F", "R'", "D", "D", "F", "R", "R", "F", "F", "R", "R", "L", "L", "F'", "R", "R"]
    for i in s:
        c.RotateWithNotation(i)
    c._readable_solution = []
    print(s)
    #print(c)
    return c
    #print(c)

def EnterScramble():
    c = Cube()
    move = "placeholder"
    s = []
    while(move != ""):
        move = raw_input()
        if move != "":
            s.append(move)
    #print(s)
    for i in s:
        c.RotateWithNotation(i)
    c._readable_solution = []
    #print(c)
    return c

def CreateScramble():
    c = Cube()
    s = []
    moves = ["U", "D", "L", "R", "F", "B", "U'", "D'", "L'", "R'", "F'", "B'"]
    counter = 0
    #inc = lambda n : (n+3) % 12
    while counter < 30:
        i = random.randint(0, 11)
        #m = moves[i]
        #print(s)
        if len(s) == 0:
            s.append(moves[i])
            counter += 1
        else:
            j = len(s)-1
            doub = 0
            #mix = 0
	    while j >= 0:
                #print(moves[i], c._inverts[s[j]], s[j])
                if s[j] == moves[i]:
                    doub += 1
                    j -= 1
                    if doub == 2:
                        break
                else:
                #print(doub)

                #if (s[j] == i and s[j-1] == i) or (s[j] == c._inverts[moves[i]]) or ():
                #    break
                #if doub > 1 or moves[i] == c._inverts[s[j]]:
                    if moves[i] == c._inverts[s[j]]:
                        break
                #elif doub == 1 or s[j] == c._not_effected[s[j][0]]:
                    elif s[j][0] == c._not_effected[moves[i][0]]:
                        j -= 1
                    else:
                    #print(s)
                    #print("Adding '" + moves[i] + "'")
                        s.append(moves[i])
                        counter += 1
                        break
            #if s[len(s)-1] == c._inverts[m] or (len(s) > 2 and s[len(s)-1] == m and s[len(s)-2] == m):
            #    continue

            #else:
            #    s.append(m)
        #counter += 1
        #flip = random.random()
        #if flip > 0.5:
        #    m += "'"
        #print("Previous: %s\tCurrent: %s\tInvert: %s" % (prev, m, c._inverts[m]))
        #print(not prev == c._inverts[m])
        #if m == prev:
        #    if count < 2:
        #        count += 1
        #else:
        #    if prev != "":
        #        for _ in range(count):
        #            s.append(prev)
        #    count = 1
            #print("Previous: %s\tCurrent: %s\tInvert: %s" % (prev, m, c._inverts[m]))
            #print(not prev == c._inverts[m])
        #    if not prev == c._inverts[m]:
        #        prev = m
        #    
        #if not (len(s) > 0 and s[len(s)-1] == c._inverts[m]) or (len(s) > 1 and s[len(s)-1] != m and s[len(s)-2] != m):
        #    s.append(m)

    #print("Scramble:")
    #print(s)

    #s = ["D", "L", "R'", "B", "B", "U'", "F'", "L'", "U'", "B'", "U'", "B", "L'", "D", "U'", "D", "R", "B", "L", "D"]
    #s = ["B'", "F'", "L'", "U", "B", "U", "D", "R'", "D", "U", "L", "D'", "R", "L", "D", "U'", "L'", "U'", "L'", "B"]

    s = c._cleanUpSolution(s)

    for x in s:
        c.RotateWithNotation(x)
    c._readable_solution = []

    #s = c._cleanUpSolution(s)
    nice_s = "" + s[0]
    for i in range(1, len(s)):
        nice_s += " " + s[i]
    print("Scramble:")
    print(nice_s)

    return c

def TestLayerRotation(d, l):
    c = Cube()

    for s in c._layers[l]:
        print(c._cube[s].colour)
    for _ in range(4):
        c._rotateLayer(d, l)
        print("")
        for s in c._layers[l]:
            print(c._cube[s].colour)

def CheckAlgCorrectness():
    y = 0
    c = Cube()
    f = open("F2LAlgs.txt", "r")
    f2 = open("F2LValues.txt", "r")
    
    currentPair = [1, 2, 3, 4, 5]
    slot = [1, 2, 3, 4, 5]
    colours = [1, 2, 3, 4, 5]
    
    for line in f:
        c = Cube()
        y += 1
        print(str(y) + ":"),
        v = f2.readline().split("\n")[0].split("\r")[0].split(", ")
        currentPair = [v[0], v[1], v[2], v[3], v[4]]
        slot = [v[5], v[6], v[7], v[8], v[9]]

        for i in range(len(slot)):
            index = int(slot[i])
            colours[i] = c._cube[index].colour
            c._cube[index].colour = "X"

        #if y == 281:
        #    print(currentPair)
        #    print(slot)
        #    print(c)

        for i in range(len(slot)):
            index = int(slot[i])
            other = int(currentPair[i])
            #temp = c._cube[index].colour
            #colours[i] = temp
            #if y == 15:
            #    print(other)
            #    print(slot)
            #c._cube[index].colour = "X"
            #if y == 281:
            #    print(other)
            c._cube[other].colour = colours[i]

        #if y == 870:
        #    print(line)
        
        #print(line)
        l = line.split("\n")[0].split("\r")[0].split(" ")
        #print(l)
        for x in l:
            c.RotateWithNotation(x)

        for i in range(len(slot)):
            if c._cube[int(slot[i])].colour != colours[i]:
                print("Error")
                print(v)
                print(l)
                #print(y)
                #print(colours)
                print(c)
                return
        print("CORRECT")
    print("FIN")

def CheckOLLAlgs():
    f = open("OLLValues.txt", "r")
    f2 = open("OLLAlgs.txt", "r")
    x = {"1":"R", "0":"X"}
    y = 0

    top_squares = [0, 1, 2, 7, 8, 3, 6, 5, 4]
    side_squares = [51, 50, 49, 29, 28, 27, 20, 19, 18, 11, 10, 9]

    for line in f:
        y += 1
        c = Cube()
        l = line.split("\n")[0].split("-")
        alg = f2.readline().split("\n")[0].split(" ")
        for i in range(len(l[0])):
            c._cube[top_squares[i]].colour = x[l[0][i]]
        for i in range(len(l[1])):
            c._cube[side_squares[i]].colour = x[l[1][i]]
        
        #if y == 33:
        #    print(c)

        for a in alg:
            c.RotateWithNotation(a)
       
        for i in top_squares:
            if c._cube[i].colour != "R":
                print("ERROR: " + str(y))
                print(l)
                print(alg)
                print(c)
                return

    f.close()
    f2.close()
    print("FIN")

def CheckPLLAlgs():
    f = open("PLLValues.txt", "r")
    f2 = open("PLLAlgs.txt", "r")
    num_to_col = {"1":"W", "2":"G", "3":"Y", "4":"B"}
    side_positions = [51, 50, 49, 29, 28, 27, 20, 19, 18, 11, 10, 9]
    y = 0

    for line in f:
        y += 1
        cu = Cube()
        l = line.split("\n")[0].split("-")
        l2 = []
        for item in l:
            for item2 in item:
                l2.append(item2)

        for i in range(len(side_positions)):
            cu._cube[side_positions[i]].colour = num_to_col[l2[i]]

        a = int(l[0][0]) * (int(l[0][1]) + int(l[0][2]))
        b = int(l[1][0]) + (int(l[1][1]) * int(l[1][2]))
        c = (int(l[2][0]) * int(l[2][1])) + int(l[2][2])
        d = (int(l[3][0]) + int(l[3][1])) * int(l[3][2])

        val = a**c + b**d
        alg = cu._pll_r.get(str(val))
        a = alg.split(" ")
        for item in a:
            cu.RotateWithNotation(item)
        
        for i in range(9):
            if cu._cube[i].colour != "R":
                print("ERROR:")
                print(y)
                print(l)
                print(alg)
                print(cu)
                return

    f.close()
    f2.close()
    print("FIN")

if __name__ == '__main__':
    main()