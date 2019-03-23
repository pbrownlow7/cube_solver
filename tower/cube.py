import math
import time
import random
import redis
import copy

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

    def getNeighbours(self, index):
        return self._elements[index][1]

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
    Cube is the main cube and holds all the functions for representing and manipulating the cube.

    VARIABLES:
    _graph - a graph representing the cube. It has the structure of a node being a group of three stickers on the cube and the edges are all the possible nodes that
             can be reached from that node.
    _middle - a graph representing the middle part of the cube. It has the same structure as _graph
    _opposites - maps a colour of a face to the face colour on the opposite side of the cube
    _translation - maps a face colour to its letter representation for rotation
    _inverts - the opposite rotation to a letter representation
    _not_effected - maps a letter representation to the letter representation that is not affected by its rotation
    _cube - a list representing the stickers on the cube
    _r - the database that holds the F2L algorithms
    _oll_r - the database that holds the OLL algorithms
    _pll_r - the database that holds the PLL algorithms
    _wide_rotations - maps the letter representation of a wide rotation to its parameters for rotation
    _face_rotations - maps the letter representation of a face rotation to its parametes for rotation
    _cube_rotations - maps the letter representation of a cube rotation to its parameters for rotation
    """

    def __init__(self):
        self._graph = buildGraph("../data/config.txt")
        self._middle = buildGraph("../data/middle_config.txt")
        self._opposites = {"R":"O", "W":"Y", "G":"B", "Y":"W", "O":"R", "B":"G"}
        self._translation = {"R":"U", "W":"L", "G":"F", "Y":"R", "O":"D", "B":"B"}
        self._inverts = {"U": "U'", "D": "D'", "L": "L'", "R": "R'", "F": "F'", "B": "B'", "U'": "U", "D'": "D", "L'": "L", "R'": "R", "F'": "F", "B'": "B", "M":"M'", "M'":"M"}
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
        """
        Returns the steps to solving the first stage of the solve
        """
        
        return self._solveCross()

    def _solveCross(self):
        """
        Main funciton of the cross solve. Starts by getting the positions of each of the cross squares. Checks whether on of them is in the bottom layer. If not
        then the closest square to the bottom layer is found and inserted. After that the anchor square is found - which is the square that the positions of all
        other cross squares are based off. Next it finds where the other cross squares are supposed to go in relation to this anchor - called anchorTargets. It then
        finds the shortest path to the respective anchor targets. It then changes this path into its letter representation, passing in squares that are already in the
        correct position so they don't get moved. This is repeated until every cross square is in the bottom layer in the correct position inrespect to the other
        cross squares. Then the bottom layer is turned until it's in the correct position.

        #VARIABLES:
        cross_turns - the turns undertaken while solving the cross
        positions - the positions of the cross squares in the form (x, y) where x is the index in _graph and y is the index in _cube. positions[0] is the cross colour
                    sticker positions, positions[1] is the corresponding colour sticker positions for those squares
        cross_positions - takes on positions[0]
        coloured_positions - takes on positions[1]
        sq_in_bottom - True if there's a square in the bottom layer, False otherwise
        close - holds the index (in cross_positions) of the square that is closest to the bottom layer, and the path to this target
        close_index - takes on close[0] (closest square's index)
        path - takes on close[1] (path to the bottom layer)
        p - the letter representation of path
        anchor_index - the index (in cross_positions) of the cross square in the bottom layer to base the other cross square positions off
        cross_solved - False until each piece is in the correct orientation in the bottom layer
        anchor_targets - the targets in the bottom layer for each cross square not inserted yet represented as a dictionary where the key is the colour of the
                        corresponding sticker on the cross square and the value is a truple ((index in _graph, index in _cube), index in cross_positions)
        both_paths - returns the path from the closest cross square to the bottom layer, the path from that squares anchor_target, the starting position of the cross
                    square, and the starting position of the anchor_target square
        in_position - the colours of all the cross squares in position
        correct_path - the letter representation of the path the insert the closest cross square
        actual_turns - used to clean up cross_turns
        """
        
        cross_turns = []
        cross_colour = "O" #TODO: move to global variable
        positions = self._findCrossSquares()
        cross_positions = positions[0]
        coloured_positions = positions[1]
        sq_in_bottom = False
        for i in range(len(cross_positions)):
            if cross_positions[i][1] >= 37 and cross_positions[i][1] <= 43:
                sq_in_bottom = True
                break
        if not sq_in_bottom:
            close = self._closestInitialSquare(cross_positions)
            close_index = close[0]
            path = close[1]
            built_path = []
            current = cross_positions[close_index][0]
            for item in path:
                built_path.append((current, [item]))
                current = item
            p = self._pathNotation(cross_positions[close_index][0], path, [])
            positions = self._rotateReturnPosition(cross_positions, coloured_positions, p, [], built_path)
            cross_positions = positions[0][0]
            coloured_positions = positions[0][1]
            for i in positions[1]:
                cross_turns.append(i)

        anchor_index = self._findAnchor(cross_positions, coloured_positions)
        cross_solved = False
        bottom_layer = ['16', '17', '18', '19']
        while not cross_solved:
            anchor_targets = self._getAnchorTargets(cross_positions, coloured_positions, anchor_index)
            both_paths = self._decideOnBestPath(anchor_targets, cross_positions, coloured_positions, anchor_index)
            if not both_paths:
                break
            in_position = self._findInPosition(anchor_targets, cross_positions, coloured_positions)
            in_position.append(coloured_positions[anchor_index][2])
            correct_path = self._decidePath(both_paths, in_position)
            positions = self._rotateReturnPosition(cross_positions, coloured_positions, correct_path[0], in_position, correct_path[1])
            cross_positions = positions[0][0]
            coloured_positions = positions[0][1]
            for i in positions[1]:
                cross_turns.append(i)
            anchor_targets = self._getAnchorTargets(cross_positions, coloured_positions, anchor_index)
            in_position = self._findInPosition(anchor_targets, cross_positions, coloured_positions)
            in_position.append(coloured_positions[anchor_index][2])
            if len(in_position) == 4:
                cross_solved = True

        buddy = self._graph.getBuddy(bottom_layer[0])
        buddy_i = self._graph.getElements(buddy)[1]
        center = (((buddy_i / 9) + 1) * 9) - 1
        turns = []
        while self._cube[buddy_i].colour != self._cube[center].colour:
            self.RotateWithNotation("D")
            turns.append("D")
            buddy = self._graph.getBuddy(bottom_layer[0])
            buddy_i = self._graph.getElements(buddy)[1]
            center = (((buddy_i / 9) + 1) * 9) - 1

        actual_turns = []
        i = 0
        while i < len(cross_turns):
            if (i+1 < len(cross_turns) and cross_turns[i] == cross_turns[i+1]) and (i+2 < len(cross_turns) and cross_turns[i] == cross_turns[i+2]):
                actual_turns.append(self._inverts[cross_turns[i]])
                i += 3
            elif (i+1 < len(cross_turns) and cross_turns[i] == cross_turns[i+1]):
                actual_turns.append(cross_turns[i]+"2")
                i += 2
            elif i+1 < len(cross_turns) and cross_turns[i] == self._inverts[cross_turns[i+1]]:
                i += 2
                continue
            else:
                actual_turns.append(cross_turns[i])
                i += 1

        if len(turns) > 0:
            if len(turns) == 3:
                t = turns[0] + "'"
            elif len(turns) == 2:
                t = turns[0] + "2"
            else:
                t = turns[0]
            actual_turns.append(t)

        return actual_turns

    def _rotateReturnPosition(self, cross_positions, coloured_positions, path, in_position, path_indices):
        """
        Rotates the cube based on path. It checks whether one of the turns in path moves one of the correctly oriented cross squares in the bottom out of position and
        corrects it after the current cross square is moved into position. It then finds the new positions of the cross squares and updates the values in positions. It
        keeps the positioning of the squares in positions consistent for simplicity for other functions. Returns the updated values for cross_positions and
        coloured_positions and the letter representation of the moves taken

        #VARIABLES:
        old_cross - holds the values of the old cross positions
        old_coloured - holds the values of the old coloured stickers of each cross square
        collisions - holds the values of any collisions that happen during turning
        taken - holds the letter representation of every turn taken, including readjustments for collisions
        new_positions - holds the new values for cross positions and their corresponding coloured stickers
        """
        
        cross_colour = "O" #TODO: make global
        old_cross = cross_positions
        old_coloured = coloured_positions
        collisions = []
        taken = []
        for t in range(len(path)):
            if path[t][0] != "D":
                neigh = self._graph.getNeighbours(path_indices[t][0])
                for n in range(len(neigh)):
                    if neigh[n] == path_indices[t][1][0]:
                        op = n
                        break
                if self._returnCollision(['16', '17', '18', '19'], op, path_indices[t][0], in_position):
                    collisions.append(t)
            self.RotateWithNotation(path[t])
            taken.append(path[t])
        for t in collisions:
            self.RotateWithNotation(self._inverts[path[t]])
            taken.append(self._inverts[path[t]])
        new_positions = self._findCrossSquares()
        for i in range(len(old_coloured)):
            for j in range(len(new_positions[1])):
                if new_positions[1][j][2] == old_coloured[i][2]:
                    old_coloured[i] = new_positions[1][j]
                    old_cross[i] = new_positions[0][j]
        return ((old_cross, old_coloured), taken)
        
    def _findCrossSquares(self):
        """
        Runs through _graph checking if the elements in the center of the node is the same as cross_colour, taking note of their index in _graph and _cube. It also
        takes note of the positions of the corresponding colour sticker, along with the colour of the sticker. Returns these values

        #VARIABLES:
        cross_positions - the index of the cross square in _graph and _cube
        buddy_positions - the index of the corresponding colour sticker in _graph and _cube, as well as the colour
        """
        
        cross_colour = "O" #TODO: make global
        cross_positions = []
        buddy_positions = []
        for i in range(len(self._graph._elements)):
            sq_index = self._graph.getElements(str(i))[1]
            if self._cube[sq_index].colour == cross_colour:
                bud_g = self._graph.getBuddy(str(i))
                bud_e = self._graph.getElements(bud_g)[1]
                buddy_positions.append((bud_g, bud_e, self._cube[bud_e].colour))
                cross_positions.append((str(i), sq_index))
        return (cross_positions, buddy_positions)

    def _closestInitialSquare(self, positions):
        """
        Runs through _graph looking for cross squares and takes note of the distance of each of these squares to the bottom layer. Returns the index (in
        cross_positions) of the closest square and the path to the bottom_layers

        #VARIABLES:
        distances - the paths of each of the cross squares to the bottom_layer
        closest - the number of moves of the closest square
        index - the index of the closest square
        """
        
        bottom_layer = ['16', '17', '18', '19']
        distances = []
        for sq in positions:
            distances.append(self._bfs(sq[0], bottom_layer))
        closest = None
        index = 0
        for i in range(len(distances)):
            if closest == None or len(distances[i]) < closest:
                closest = len(distances[i])
                index = i
        return (index, distances[index])

    def _bfs(self, initial, target):
        """
        Implementation of the Breadth-First Search algorithm to search for the shortest path between a cross square and its target position in the bottom layer. First
        has to check if the initial square is in the bottom layer, because if it is then it will not be able to find a correct path to its target, so it must be
        moved out. After that it then runs the actual Breadth-First Search algorithm, returning the path to it.

        #VARIABLES:
        bottom_layer - used to check if the square is in the bottom layer
        found - bool to tell if the target has been found
        target_found - the index in _graph of the target when it is found
        q - queue used to keep track of the next node to check
        path - the path taken from each node, the key is the node and the value is the node from which you came from to get to the current node
        visited - a list of all the visited nodes so we don't continuously check the same node
        current - the current node to check
        neigh - the neighbours of the current node
        """
        
        bottom_layer = ['16', '17', '18', '19']
        found = False
        target_found = None
        q = Queue()
        path = {}
        visited = [initial]
        current = initial
        path[initial] = None

        if current in bottom_layer:
            neigh = self._graph.getNeighbours(current)
            for n in neigh:
                if n not in bottom_layer:
                    path[n] = current
                    if current in target:
                        return [n, current]
                    current = n
                    break
        
        while not found:
            neigh = self._graph.getNeighbours(current)
            for n in range(len(neigh)):
                if found:
                    break
                if neigh[n] not in visited:
                    q.enqueue(neigh[n])
                    visited.append(neigh[n])
                    path[neigh[n]] = current
                    for i in target:
                        if i == neigh[n]:
                            found = True
                            target_found = neigh[n]
                            break
            current = q.dequeue()
        return self._buildPath(path, target_found)

    def _buildPath(self, path, current):
        """
        Takes the dictionary from _bfs and builds the path taken from the initial square to the target. Simply adds current to the path list if it not None, then
        updates current to be the value at path[current]

        #VARIABLES:
        p - the path taken from the initial square to its target
        path - a dictionary representing the path from _bfs
        current - the target node, where the trail to the path starts
        """

        p = []
        while True:
            if path[current] != None:
                p = [current] + p
                current = path[current]
            else:
                break
        return p

    def _pathNotation(self, index, path, in_position):
        #TODO: clean up - remove in_position and commented out variables (bottom_layer and correntions)
        """
        Takes the path derived from _buildPath and changes it from the indices of the squares in _graph to their actual letter representation in the cube. Does so by
        looping through path, getting the neighbours of the current node in question, taking the matching neighbour and determining which way it moves (clockwise or
        anticlockwise)

        #VARIABLES:
        notation - translation from each index to its corresponding letter representation
        p - p in letter format
        current - the current node in the path
        path - the path in indices format from the initial square to its target
        index - the index in _graph of the initial square
        """
        
        #bottom_layer = ['16', '17', '18', '19']
        notation = {'0':['U', 'B'], '1':['U', 'R'], '2':['U', 'F'], '3':['U', 'L'], '4':['L', 'U'], '5':['U', 'F'], '6':['L', 'D'], '7':['L', 'B'], '8':['F', 'U'], \
                    '9':['F', 'R'], '10':['F', 'F'], '11':['F', 'L'], '12':['R', 'U'], '13':['R', 'B'], '14':['R', 'D'], '15':['R', 'F'], '16':['D', 'F'], \
                    '17':['D', 'R'], '18':['D', 'B'], '19':['D', 'L'], '20':['B', 'D'], '21':['B', 'R'], '22':['B', 'U'], '23':['B', 'L']}

        p = []
        current = index
        #corrections = []
        for i in path:
            neigh = self._graph.getNeighbours(current)
            for n in range(len(neigh)):
                if neigh[n] == i:
                    t = notation[current][n/2]
                    """
                    This checks if the matching node is a clockwise or anticlockwise rotation from the current node. Becuase the rotations are represented like this:
                    [clockwise_face, anticlockwise_face, clockwise_neighbour, anticlockwise_neighbour], the turn is clockwise if it's even and anticlockwise if it's
                    odd
                    """
                    if n%2 == 1:
                        t += "'"
                    p.append(t)
                    current = neigh[n]
                    break
        return p

    def _returnCollision(self, bottom_layer, op, current, in_position):
        """
        Determines whether the movement of one cross piece interferes and moves a solved cross piece out of its correct position, taking note of the rotation that
        caused the interference. It does this by taking all the side pieces of the affected squares during the rotation and checks if they are both in the bottom
        layer and if they are correctly oriented cross pieces

        #VARIABLES:
        bottom_layer - the indices in _graph of the bottom layer
        op - the index of the operation that rotated the cube
        current - the index of the square that cause the rotation
        in_position - list of the cross pieces correctly oriented
        buddy_index - the index of the sticker that is on the same square as the current sticker being checked
        cube_i - the index in _cube of the current square
        buddy_i the index in _cube of the current square's buddy
        bottom_colour - the colour of the current sticker
        buddy_clr - the colour of the current sticker's buddy
        """ 
        for i in range(4):
            buddy_index = self._graph.getBuddy(current)
            if current in bottom_layer or buddy_index in bottom_layer:
                cube_i = self._graph.getElements(current)[1]
                buddy_i = self._graph.getElements(self._graph.getBuddy(current))[1]
                bottom_clr = self._cube[cube_i].colour
                buddy_clr = self._cube[buddy_i].colour
                if (bottom_clr == "O" and buddy_clr in in_position) or (buddy_clr == "O" and bottom_clr in in_position):
                    return True
            current = self._graph.getNeighbours(current)[op]
        return False

    def _findAnchor(self, cross_positions, coloured_positions):
        """
        Finds the cross square in the bottom layer that will be used as the reference point for the positioning of the other cross squares. Goes through the bottom
        layer and returns index in cross_positions of the first cross square it finds

        #VARIABLES:
        cross_positions - the positions of the cross positions
        coloured_positions - the positions of the corresponding coloured positions
        bottom_layer - the coordinates of the bottom layer
        anchor - the index in cross_positions of the anchor
        """
        
        bottom_layer = ['16', '17', '18', '19']
        anchor = None
        for c in range(len(cross_positions)):
            for i in range(len(bottom_layer)):
                if cross_positions[c][0] == bottom_layer[i]:
                    anchor = c
                    return anchor

    def _getAnchorTargets(self, cross_positions, coloured_positions, anchor_index):
        """
        Returns the positions of the cross squares that are not the anchor in respect to this anchor. First it gets the correct position in the bottom layer of the
        anchor. This position is the index in both _graph and _cube. Next it rotates the cube clockwise in respect to the bottom layer, taking note of the order of
        the colours of the center squares of each of the buddies of the bottom layer squares. This order represents the positioning of the other cross squares relative
        to the anchor. It then starts at the current position of the anchor square and rotates clockwise, adding the colour as the key and the index in both _graph
        and _cube, along with the index in cross_positions of the corresponding cross square.

        #VARIABLES:
        cross_positions - the positions of teh cross positions
        coloured_positions - the positions of the corresponding coloured stickers
        anchor_index - the index of the anchor square in _graph
        bottom_layer - the positions of the bottom layer squares
        anchor_position - the index of the anchor in bottom_layer, as well as the index in _cube
        colour_order - the actual order of the colours in repect to the anchor
        order - the order in respect to the current position of the anchor in the bottom layer
        """
        
        bottom_layer = ['16', '17', '18', '19']
        anchor_position = None
        buddy = self._graph.getElements(self._graph.getBuddy(cross_positions[anchor_index][0]))[1]
        buddy_colour = self._cube[buddy].colour
        for i in bottom_layer:
            buddy_i = int(self._graph.getElements(self._graph.getBuddy(i))[1])
            center = (((buddy_i / 9) + 1) * 9) - 1
            if self._cube[center].colour == buddy_colour:
                anchor_position = (i, self._graph.getElements(i)[1])
                break
        current = anchor_position[0]
        colour_order = []
        for _ in range(3):
            current = self._graph.getNeighbours(current)[0]
            current_cube = self._graph.getElements(self._graph.getBuddy(current))[1]
            center = (((current_cube / 9) + 1) * 9) - 1
            current_colour = self._cube[center].colour
            colour_order.append(current_colour)
        current = cross_positions[anchor_index][0]
        order = {}
        for i in range(3):
            current = self._graph.getNeighbours(current)[0]
            elem = self._graph.getElements(current)[1]
            index = None
            for j in range(len(coloured_positions)):
                if coloured_positions[j][2] == colour_order[i]:
                    index = j
                    break
            order[colour_order[i]] = ((current, elem), index)
        return order

    def _decideOnBestPath(self, anchor_targets, cross_positions, coloured_positions, anchor_index):
        """
        Determines which cross square is the closest to being in its solved space. Does so by first gettig the cross squares that should be excluded - the ones already
        in position. It then loops through cross_positions, taking the ones that are not excluded and determining their path to their solved slot. It does this in two
        steps. First it finds the path of the cross square to the closest square in the bottom layer, not taking into account its target position with respect to the
        anchor square. Next it takes its target square and finds the path from this to where the just mentioned bottom layer square. It then finds the square with
        the least number of moves to its solved state.

        #VARIABLES:
        anchor_targets - the positions of the cross squares in respect to the anchor square
        cross_positions - the positions of the cross squares
        coloured_positions - the positions of the corresponding stickers
        anchor_index - the index of the anchor square in _graph
        bottom_layer - the indices in _graph of the bottom layer
        exclude - the cross squares that are already in the correct position and should be excluded from path determining
        path_to_bottom - list containing the paths of each cross square not excluded from their closest bottom layer square
        target_to_position - lsit containing the paths of the anchor position of each cross square to the target position from path_to_bottom
        target - the index of the bottom layer position found by taking the final value of path
        clr - the sticker colour of the current cross square's anchor position
        least - the length of the shorstest path
        index - the index in path_to_bottom and target_to_positions of the shortest path
        """
        
        bottom_layer = ['16', '17', '18', '19']
        exclude = self._findInPosition(anchor_targets, cross_positions, coloured_positions)
        exclude.append(coloured_positions[anchor_index][2])
        if len(exclude) == 4:
            return None
        path_to_bottom = []
        target_to_position = []
        for i in range(len(cross_positions)):
            if coloured_positions[i][2] not in exclude:
                path = self._bfs(cross_positions[i][0], bottom_layer)
                path_to_bottom.append((path, cross_positions[i][0]))
                target = path[-1]
                clr = coloured_positions[i][2]
                bottom_path = self._findBottomToTarget(anchor_targets[clr][0][0], target)
                target_to_position.append((bottom_path, anchor_targets[clr][0][0]))
        least = None
        index = None
        for i in range(len(path_to_bottom)):
            if least == None or (len(path_to_bottom[i][0]) + len(target_to_position[i][0])) < least:
                least = len(path_to_bottom[i][0]) + len(target_to_position[i][0])
                index = i
        return (path_to_bottom[index][0], target_to_position[index][0], path_to_bottom[index][1], target_to_position[index][1])

    def _findBottomToTarget(self, start, target):
        """
        Determines the path from start (the position of the anchor_target of the current cross square in question) and the target of said cross_square. We can't use
        _bfs here because of the way it is designed, in that it will move the start square out of the bottom layer at the beginning of the search, which here wouldn't
        make sense. Instead it just starts at the start square and rotates the bottom layer until it finds teh correct position, return the path undertaken

        #VARIABLES:
        start - the position of the anchor_target of the current cross square
        target - the target of the current cross square
        path - the path taken from start to target
        """
        
        if start == target:
            return []
        path = []
        neigh = self._graph.getNeighbours(start)
        if neigh[1] == target:
            path.append(neigh[1])
        elif neigh[0] == target:
            path.append(neigh[0])
        else:
            path.append(neigh[0])
            new = neigh[0]
            neigh = self._graph.getNeighbours(new)
            path.append(neigh[0])
        return path

    def _findInPosition(self, anchor_targets, cross_positions, coloured_positions):
        """
        Finds the cross squares that are correctly oriented in the bottom layer. Simply takes the the values in anchor_targets and cross_positions and compares them

        VARIABLES:
        anchor_targets - positions of the target positions relative to the anchor for each cross square
        cross_positions - positions of each cross_position
        coloured_positions - positions of each corresponding sticker
        """
        
        in_position = []
        for key in anchor_targets:
            i = anchor_targets[key][1]
            if anchor_targets[key][0][0] == cross_positions[i][0]:
                in_position.append(coloured_positions[i][2])
        return in_position

    def _decidePath(self, both_paths, in_position):
        """
        Builds the path of the closest cross square based on both_paths. It builds the path by doing a check first, taking an action or not based on this check, moving
        the bottom layer into the target position, and finally also moving the cross square itself into the target position. The check is to see whether the square
        piece is in the bottom layer or not. If it is, then the first move will be to move the piece out of this position, so it executes the first move in square_path
        and then deletes it so it doesn't get executed again

        VARIABLES:
        both_paths - contains the path for the cross square and the path for the anchor_target
        in_positions - contains the cross squares that are in position (used for _pathNotation)
        bottom_layer - the positions in _graph of the bottom layer
        square_path - holds the path of the cross square
        starting_point - the starting point of the cross square
        bottom_start - the starting point of the anchor_target
        bottom_path - the path of the anchor_target to the target
        path_to_take - the actual path to be taken (a mixture of both paths) to be returned
        path_indices - the list of the corresponding indices in _graph of the turns in path_to_take, used in _rotateReturnPosition to check if correctly oriented
                       cross squares are moved out of position
        starting_neighbour - the corresponding sticker to check if the square is in the bottom_layer
        """
        
        bottom_layer = ['16', '17', '18', '19']
        square_path = both_paths[0]
        starting_point = both_paths[2]
        bottom_start = both_paths[3]
        bottom_path = both_paths[1]
        path_to_take = []
        path_indices = []
        starting_neighbour = self._graph.getBuddy(starting_point)
        if starting_point in bottom_layer or starting_neighbour in bottom_layer:
            path_indices.append((starting_point, [square_path[0]]))
            p = self._pathNotation(starting_point, [square_path[0]], in_position)
            starting_point = square_path[0]
            for t in p:
                path_to_take.append(t)
            del square_path[0]
        if len(bottom_path) > 0:
            current = bottom_start
            for item in bottom_path:
                path_indices.append((bottom_start, [item]))
                current = item
            p = self._pathNotation(bottom_start, bottom_path, [])
            for t in p:
                path_to_take.append(t)
        if len(square_path) > 0:
            current = starting_point
            for item in square_path:
                path_indices.append((current, [item]))
                current = item
            p = self._pathNotation(starting_point, square_path, in_position)
            for t in p:
                path_to_take.append(t)
        return (path_to_take, path_indices)
        
    #Start of F2L
    def SolveF2L(self):
        """
        Returns the path to take to solve the F2L stage of the solve in the fewest number of turns based on the cross solve
        """
        
        #iself._optimisedF2L()
        return self._solveF2L()

    def _solveF2L(self):#def NonOptF2L(self):
        """
        Returns the path to take to solve the F2L stage in the quickest time, not taking into account the number of turns
        """

        algs = []
        pairs = self._getF2LPairs()#self._optimisedF2L()[0]
            
        while pairs != []:
            alg = self._calculatePair(pairs[0])
            algs.append(alg)
            a = alg.split(" ")
            for t in a:
                self.RotateWithNotation(t)
            pairs = self._getF2LPairs()#self._optimisedF2L()
           
        return algs

    def _calculatePair(self, pair):
        """
        Calculates the value associated with an F2L pair and returns the algorithm for that pair
        """
        
        a = pair[5]**pair[0]
        b = pair[1][1]**pair[6]
        c = pair[7]**pair[2][1]
        d = pair[3][1]**pair[8]
        e = pair[9]**pair[4][1]
        val = a + b + c + d + e
        alg = self._r.get(val)
        return alg

    def _getF2LPairs(self):#def _optimisedF2L(self):
        """
        Returns all unsolved F2L pair coordinates. First goes through each corner position on the cube to test for a corner piece (one that has a cross colour on it),
        taking note of the position of each of the stickers that are a part of that piece. It then finds the corresponding side piece for the corner, based on the non
        cross colour stickers on the corner. It then adds the coordinates of all these pieces into the pair list before finding the coordinates of where this pair
        is to be inserted. slot_deciders is used to determine where the pair is to be inserted. They are the coordinates of the stickers of the cross squares that
        lie either side of the corner piece's correct slot. The list is looped through until a match is found and the coordinates are then add to the pair list. It
        then checks whether the pair is already in its correct slot, where if it is not it is added to the all_pairs list, which is returned after all pairs are
        checked.

        VARIABLES:
        slot_decides - the coordinates of the colours either side of each of the corner slots, used to determine where each pair needs to go
        slot - the coordinates of the slots of each of the corners
        corner_positions - the positions of all the corners on the cube, including the other two sticker's coordinates in a clockwise manor. They are in a clockwise
                           manor so that the values for the pair are consistent
        side_positions - the positions of all the possible side pieces on the cube (must exclude bottom layer pieces)
        corner - list of the three coordinates of the current corner
        side - list of the two coordinates of the current side
        pair - list of the coordinates of the corner and side pair as well as the coordinates of the slot where they need to be inserted
        all_pairs - the list of all unsolved F2L pairs to be returned
        """
        
        cross_colour = "O"
        slot_deciders = [(14, 23), (23, 32), (32, 46), (46, 14)]
        slots = [(36, 13, 24, 12, 25), (38, 22, 33, 21, 34), (40, 31, 47, 30, 48), (42, 45, 15, 52, 16)]
        corner_positions = {0:[9, 51], 9:[51, 0], 51:[0, 9], 2:[49, 29], 49:[29, 2], 29:[2, 49], \
                            4:[27, 20], 27:[20, 4], 20:[4, 27], 6:[18, 11], 18:[11, 6], 11:[6, 18], \
                            13:[24, 36], 24:[36, 13], 36:[13, 24], 45:[15, 42], 15:[42, 45], 42:[45, 15], \
                            31:[47, 40], 47:[40, 31], 40:[31, 47], 22:[33, 38], 33:[38, 22], 38:[22, 33]}

        side_positions = {1:50, 3:28, 5:19, 7:10, 10:7, 12:25, 16:52, 19:5, 21:34, \
                          25:12, 28:3, 30:48, 34:21, 50:1, 52:16, 48:30}
        
        corner = [0, 0, 0]
        side= [0, 0]
        pair = []
        all_pairs = []

        for k in corner_positions.keys():
            if self._cube[k].colour == cross_colour:
                corner[0] = k
                corner[1] = (self._cube[corner_positions[k][0]].colour, corner_positions[k][0])
                corner[2] = (self._cube[corner_positions[k][1]].colour, corner_positions[k][1])

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

                total = abs(pair[0] - pair[5]) + abs(pair[1][1] - pair[6]) + abs(pair[2][1] - pair[7]) + abs(pair[3][1] - pair[8]) + abs(pair[4][1] - pair[9])

                """
                If total is 0 then the pair has already be inserted
                """
                if total != 0:
                    all_pairs.append(pair)

        return all_pairs

    def SolveOLL(self):
        """
        Returns the algorithm to solve the OLL stage
        """
        
        return self._solveOLL()

    def _solveOLL(self, stats=False):
        """
        Works out the value associated with the cube configuration and returns the algorithm for that value. It runs through the squares on the top layer of the cube,
        marking each square as a 0 or a 1 depending on whether the square is not the correct colour or it is, respectively. The correct colour is the opposite of that
        of the cross colour. This sequence of 0sand 1s is treated as a binary sequence and converted into an int. Before this conversion, the number of 1s is counted.
        If that number is 9, then the OLL stage is already solved and there is no need to continue. The corresponding stickers of each of the top layer squares are
        then taken into consideration and the same thing is done with them. These two integers are then multiplied together, obtaining the value for the algorithm,
        which is used to return the corresponding algorithm. Each top layer pattern maps to an algorithm, butonly in one orientation, so if no algorithm is returned
        for a given pattern, the top layer is rotated and the process is repeated until an algorithm is found, adding the number of rotations to the start of the
        algorithm

        VARIABLES:
        tops_squares - the indices in _cube of the top layer in the order they are to be checked
        side_squares - the indices in _cube of the side stickers of the top layer in the order they are to be checked
        match_colour - the colour of the top layer
        turns - the list of turns until the correct pattern is found
        top_bits - the bits associated with the top layer
        side_bits - the bits associated with the side stickers of the top layer
        num_top_bits - the number of bits that are 1 in top_bits
        top_val - the integer value of the top_bits sequence
        side_val - the integer value of the side_bits sequence
        act - the actual algorithm to be returned, including the turns that occurred to find th ecorrect pattern
        """
        
        cross_colour = "O"
        top_squares = [0, 1, 2, 7, 8, 3, 6, 5, 4]
        side_squares = [51, 50, 49, 29, 28, 27, 20, 19, 18, 11, 10, 9]
        match_colour = self._opposites[cross_colour]
        turns = []
        alg = None

        while True:
            top_bits = []
            side_bits = []
            num_top_bits = 0

            for i in top_squares:
                if self._cube[i].colour == match_colour:
                    num_top_bits += 1
                    top_bits.append(1)
                else:
                    top_bits.append(0)

            if num_top_bits == 9:
                return []

            for i in side_squares:
                if self._cube[i].colour == match_colour:
                    side_bits.append(1)
                else:
                    side_bits.append(0)
            
            top_val = self._bToI(top_bits)
            side_val = self._bToI(side_bits)
            alg_value = top_val * side_val
            alg = self._oll_r.get(str(alg_value))
            if alg != None:
                if stats:
                    f = open("../data/oll_stats.txt", "a+")
                    top = ""
                    side = ""
                    for i in top_bits:
                        top += str(i)
                    for i in side_bits:
                        side += str(i)
                    f.write(top + "-" + side + "\n")
                    f.close()
                break
            else:
                turns.append("U")
                self.RotateWithNotation("U")
        act = []
        if len(turns) > 0:
            if len(turns) == 3:
                t = turns[0] + "'"
            elif len(turns) == 2:
                t = turns[0] + "2"
            else:
                t = turns[0]
            act.append(t)

        a = alg.split(" ")
        for i in a:
            self.RotateWithNotation(i)
            act.append(i)
        return act

    def _bToI(self, bits):
        """
        Function that returns the integer value associated with the bit sequence

        VARIABLES:
        bits - the list of 0s and 1s to be converted
        total - the integer value to be returned
        """
        
        total = 0
        for bit in range(len(bits)):
            total += bits[bit] * (2**bit)
        return total

    def SolvePLL(self):
        """
        Returns the steps involved in solving the PLL stage
        """
        
        return self._solvePLL()

    def _solvePLL(self, stats=False):
        """
        Works out the value of the pattern on the side stickers of the top layer and returns the algorithm associated with this value. First it checks if the PLL stage
        is already solved, if so there is no need to continue. If not then the side stickers of the top layer are checked. When a new colour is seen, it is added to
        a dictionary where the colour is the key and the value is the number in the sequence of new colours that have been seen. This number is then added into the
        correct list, by taking the index of the value in side_positions and dividing by 3, as the side stickers are in groups of 3. These values are then used in
        an equation to determine the unique value that represents the pattern. This pattern is then used to return the corresponding algorithm, again if no algorithm
        is returned, the top layer is rotated until a recognizable pattern is found

        VARIABLES:
        turns - the rotations undertaken to find a recognizable patter is found
        side_positions - the indices in _cube of the side stickers of the top layer
        l - the number associated with each sticker in each of the four groups
        cols - the colours and their associated sequence number in the pattern
        val - the unique value associated with the pattern
        act - the actual algorithm that gets returned
        """
        
        if (self._cube[51].colour == self._cube[50].colour and self._cube[50].colour == self._cube[49].colour) and \
            (self._cube[29].colour == self._cube[28].colour and self._cube[28].colour == self._cube[27].colour):
            return [self._alignAfterPLL()]
        alg = None
        turns = []
        side_positions = [51, 50, 49, 29, 28, 27, 20, 19, 18, 11, 10, 9]

        while alg == None:
            l = [[], [], [], []]
            cols = {}
            for i in range(len(side_positions)):
                colour = self._cube[side_positions[i]].colour
                if colour not in cols.keys():
                    cols[colour] = len(cols)+1
                l[i/3].append(cols[colour])

            a = l[0][0] * (l[0][1] + l[0][2])
            b = l[1][0] + (l[1][1] * l[1][2])
            c = (l[2][0] * l[2][1]) + l[2][2]
            d = (l[3][0] + l[3][1]) * l[3][2]

            val = a**c + b**d
            alg = self._pll_r.get(str(val))

            if alg == None:
                turns.append("U")
                self.RotateWithNotation("U")

        if stats:
            f = open("../data/pll_stats.txt", "a+")
            side = ""
            for lis in l:
                for item in lis:
                    side += str(item)
            f.write(side + "\n")
            f.close()

        act = []
        if len(turns) > 0:
            if len(turns) == 3:
                t = turns[0]+"'"
            elif len(turns) == 2:
                t = turns[0]+"2"
            else:
                t = turns[0]
            act.append(t)

        a = alg.split(" ")
        for i in a:
            self.RotateWithNotation(i)
            act.append(i)
        act.append(self._alignAfterPLL())
        return act

    def _alignAfterPLL(self):
        """
        Aligns the top layer of the cube after the PLL stage, solving the cube. Simply rotates the top layer until the cube is aligned

        VARIABLES:
        turns - the rotations undertaken
        t - the turns to be returned
        """
        
        turns = []
        while self._cube[51].colour != self._cube[52].colour:
            self.RotateWithNotation("U")
            turns.append("U")

        t = ""
        if len(turns) > 0:
            if len(turns) == 3:
                t = turns[0]+"'"
            elif len(turns) == 2:
                t = turns[0]+"2"
            else:
                t = turns[0]

        return t

    def _translateToNotation(self, state, op):
        """
        Returns the letter representation of the operation given the index in _cube of the piece being moved. Gets the center peice of the face on which the piece
        is and returns the associated value of the layer it is on.
        """
        
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
                
        return new_solution

    def _translateToMechanismInstructions(self, turns):
        letter_to_arm = {"R":("arm3", 3), "L":("arm1", 1), "U":("arm0", 0), "D":("arm4", 4), "F":("arm2", 2), "B":("arm5", 5)}
        arm_rotations = []
        for item in turns:
            d = 0
            direction = "clockwise"
            arm = letter_to_arm[item]
            if len(item) > 1 and item[1] == "'":
                direction = "anticlockwise"
                d = 1

            arm_rotations.append((arm[1], d))
            print("Rotating " + arm[0] + direction + "...")
            
            if len(item) > 1 and item[1] == "2":
                arm_rotations.append((arm[1], d))
                print("Rotating " + arm[0] + direction + "...")

        return arm_rotations

    def _ollStats(self):
        return self._solveOLL(stats=True)

    def _pllStats(self):
        return self._solvePLL(stats=True)

    def __getstate__(self):
        return self.__dict__
    
    def __setstate__(seld, d):
        self.__dict__.update(d)

    def _checkEquality(self, l1, l2):
        for i in range(len(l1)):
            if l1[i].colour != l2[i].colour:
                return False
        return True
            
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

class Node:

    def __init__(self, parent, alg):
        self._parent = parent
        self._children = []
        self._alg = alg
        self._leaf = True

    def getParent(self):
        return self._parent

    def setParent(self, p):
        self._parent = p

    def getChildren(self):
        return self._children

    def addChild(self, c):
        self._children.append(c)

    def getAlg(self):
        return self._alg

    def setAlg(self, a):
        self._alg = a

    def getLeaf(self):
        return self._leaf

    def switchLeaf(self):
        if self._leaf:
            self._leaf = not self._leaf

    def __str__(self):
        strDesc = ""
        if self.parent:
            strDesc += self.parent.alg
        else:
            strDesc += "None"

        strDesc += " ---> " + self.alg + " ---> |"

        for item in self.children:
            strDesc += "| " + item.alg + " "

        strDesc += "||"

        return strDesc

    parent = property(getParent, setParent)
    children = property(getChildren)
    alg = property(getAlg, setAlg)
    leaf = property(getLeaf)

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

def listToStr(l):
    s = "" + l[0]
    for i in range(1, len(l)):
        s += " " + l[i]
    return s

def buildOLLPLLStats():
    print("Gathering OLL/PLL statistics...")
   
    for _ in range(10000):
        c = Cube()
        scramble = CreateScramble()
        print(scramble)
    
        for r in scramble:
            c.RotateWithNotation(r)

        cross = c.SolveCross()

        f2l = c.SolveF2L()

        oll = c._ollStats()

        pll = c._pllStats()

    print("FIN")

def SolveCube():
    start = time.time()
    c = Cube()
    scramble = CreateScramble()
    scramble = ["R", "U", "R'", "U'"]
    ns = listToStr(scramble)
    print("SCRAMBLE:")
    print(ns)

    for r in scramble:
        c.RotateWithNotation(r)

    print("")
    print("SOLVE:")

    cross = c.SolveCross()
    if len(cross) > 0:
        nc = listToStr(cross)

    f2l = c.SolveF2L()

    oll = c.SolveOLL()
    if len(oll) > 0:
        no = listToStr(oll)

    pll = c.SolvePLL()
    if len(pll) > 0:
        np = listToStr(pll)

    fin = time.time()

    total = fin - start

    if len(cross) > 0:
        print(nc)
    for alg in f2l:
        print(alg)
    if len(oll) > 0:
        print(no)
    if len(pll) > 0:
        print(np)
    print("")
    print("Time taken: " + str(total))

def SolveCubeWithScramble(scramble):
    moves = ["", "", "", "", "", "", "", ""]
    start = time.time()
    c = Cube()
    scramble = scramble.split(" ")
    #scramble = ["R", "U", "R'", "U'"]
    ns = listToStr(scramble)
    #print("SCRAMBLE:")
    #print(ns)

    for r in scramble:
        c.RotateWithNotation(r)

    #print("")
    #print("SOLVE:")

    cross = c.SolveCross()
    nc = ""
    if len(cross) > 0:
        nc = listToStr(cross)
    moves[0] = nc

    f2l = c.SolveF2L()
    for i in range(len(f2l)):
        moves[i+1] = f2l[i]

    oll = c.SolveOLL()
    no = ""
    if len(oll) > 0:
        no = listToStr(oll)
    moves[5] = no

    pll = c.SolvePLL()
    np = ""
    if len(pll) > 0:
        np = listToStr(pll)
    moves[6] = np

    fin = time.time()

    total = fin - start
    moves[7] = str(total)

    return moves

    #if len(cross) > 0:
    #    print(nc)
    #for alg in f2l:
    #    print(alg)
    #if len(oll) > 0:
    #    print(no)
    #if len(pll) > 0:
    #    print(np)
    #print("")
    #print("Time taken: " + str(total))

def WebPageSolve():
    s = CreateScramble()
    ns = listToStr(s)
    print(ns)
    c = Cube()
    for r in s:
        c.RotateWithNotation(r)
    colours = []
    for co in c._cube:
        colours.append(co.colour)
    print(colours)

def main():
    WebPageSolve()
    #SolveCube()
    #SolveMultipleCubes(10000)
    #buildOLLPLLStats()

def SolveMultipleCubes(number):
    total = 0
    #for i in range(number):
    while True:
        start = time.time()
        c = Cube()
        scramble = CreateScramble()
        ns = listToStr(scramble)
        print("SCRAMBLE:")
        print(ns)

        for r in scramble:
            c.RotateWithNotation(r)

        print("")
        print("SOLVE:")

        cross = c.SolveCross()
        if len(cross) > 0:
            nc = listToStr(cross)

        f2l = c.SolveF2L()

        oll = c.SolveOLL()
        if len(oll) > 0:
            no = listToStr(oll)

        pll = c.SolvePLL()
        if len(pll) > 0:
            np = listToStr(pll)

        fin = time.time()

        total += fin - start

        if len(cross) > 0:
            print(nc)
        for alg in f2l:
            print(alg)
        if len(oll) > 0:
            print(no)
        if len(pll) > 0:
            print(np)
        print("")
    print("Time taken: " + str(total))

def CreateScramble():
    c = Cube()
    s = []
    moves = ["U", "D", "L", "R", "F", "B", "U'", "D'", "L'", "R'", "F'", "B'"]
    counter = 0
    while counter < 30:
        i = random.randint(0, 11)
        if len(s) == 0:
            s.append(moves[i])
            counter += 1
        else:
            j = len(s)-1
            doub = 0
            while j >= 0:
                if s[j] == moves[i]:
                    doub += 1
                    j -= 1
                    if doub == 2:
                        break
                else:
                    if moves[i] == c._inverts[s[j]]:
                        break
                    elif s[j][0] == c._not_effected[moves[i][0]]:
                        j -= 1
                    else:
                        s.append(moves[i])
                        counter += 1
                        break

    s = c._cleanUpSolution(s)

    c._readable_solution = []

    return s

"""def TestLayerRotation(d, l):
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
    f = open("../data/F2LAlgs.txt", "r")
    f2 = open("../data/F2LValues.txt", "r")
    
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
    f = open("../data/OLLValues.txt", "r")
    f2 = open("../dataOLLAlgs.txt", "r")
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
    f = open("../data/PLLValues.txt", "r")
    f2 = open("../data/PLLAlgs.txt", "r")
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
    print("FIN")"""

if __name__ == '__main__':
    main()
