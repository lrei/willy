import sys
from copy import deepcopy

class SokoMap:
    def __init__(self):
        self.sm = []

        # Values of map pieces
        self.goal = '.'
        self.player = '@'
        self.block = '$'
        self.space = ' '
        self.wall = '#'
        self.blockOnGoal = '*'
        self.playerOnGoal = '!'
        self.deadlock = 'x'
        self.playerOnDeadlock ='+'

        self.gVal = 0
        self.fVal = 0

        self.parent = None
        self.moveList = []

    def __eq__(self, other):
        if isinstance(other, SokoMap):
            return self.sm == other.sm
        return NotImplemented

    def setMap(self, m):
        self.sm = m

    def setG(self, val):
        self.gVal = val

    def getG(self):
        return self.gVal

    def setF(self, val):
        self.fVal = val

    def getF(self):
        return self.gVal

    def setParent(self, parent):
        self.parent = parent

    def readMap(self, fileName):
        # read from txt map file
        mapFile = open(fileName, 'r')
        temp = mapFile.readlines()
        SokoMap = [] # in memory map representation: list of lists of chars
        for line in temp:
            SokoMap.append(list(line)[0:-1]) # removes newline

        while SokoMap[-1] == ['\n'] or SokoMap[-1] == []:
             # remove last "line" (empty, original only had a newline)
            SokoMap.pop()

        self.sm = SokoMap

    def getMap(self):
        return self.sm

    def printMap(self):
        #y = len(self.sm)
        #x = len(self.sm[0])

        for line in self.sm:
            print line
            # for c in line:
            #     print c,
            # print

    def getSomething(self, something):
        result = []
        y = 0
        for l in self.sm:
            x = 0
            for i in l:
                if i == something:
                    result.append((x,y))
                x = x + 1
            y = y + 1

        return result

    def getGoals(self):
        total = []
        total.extend(self.getSomething(self.goal))
        total.extend(self.getSomething(self.blockOnGoal))
        total.extend(self.getSomething(self.playerOnGoal))
        return total

    def getBlocks(self):
        total = []
        total.extend(self.getSomething(self.block))
        total.extend(self.getSomething(self.blockOnGoal))
        return total

    def getUnplacedBlocks(self):
        return self.getSomething(self.block)

    def getPlayer(self):
        if len(self.getSomething(self.player)) is not 0:
            return self.getSomething(self.player)[0]
        elif len(self.getSomething(self.playerOnDeadlock)) is not 0:
            return self.getSomething(self.playerOnDeadlock)[0]
        else:
            return self.getSomething(self.playerOnGoal)[0]

    def getWalls(self):
        return self.getSomething(self.wall)

    def getDeadlocks(self):
        return self.getSomething(self.deadlock)

    # def simplifyMap(self, block, goal):
    #     simpleMap = self.sm
    #
    #     for x in self.getBlocks() and x != block:
    #         simpleMap[x[1]][x[0]] = self.space
    #     for x in self.getGoals() and x != goal:
    #         simpleMap[x[1]][x[0]] = self.space
    #
    #     m = SokoMap()
    #     m.setMap(simpleMap)
    #     return m

    def isLegal(self, nplayer):
        (nx, ny) = nplayer
        (x, y) = self.getPlayer()

        #self.printMap()


        if nx < 0 or ny < 0 or ny >= len(self.sm) or nx >= len(self.sm[ny]):
            return False

        if self.sm[ny][nx] == self.wall:
            return False # cant move into a wall

        if self.sm[ny][nx] == self.block or self.sm[ny][nx] == self.blockOnGoal:
            # is trying to push a block
            # the only way this works is if the space after the block is free
            # or a goal so we calculate where the block is going to be pushed
            # into and see if it's "open"

            xdiff = nx - x
            ydiff = ny - y

            bx = nx + xdiff
            by = ny + ydiff


            # print "x,y=",x,y
            # print "nx,ny=",nx,ny
            # print self.sm[ny][nx]
            # print "bx,by=",bx, by
            # print self.sm[by][bx]

            if (self.sm[by][bx] == self.block or
                self.sm[by][bx] == self.wall or
                self.sm[by][bx] == self.blockOnGoal or
                self.sm[by][bx] == self.deadlock
                ):
                return False


        # everything is OK
        return True

    def isSolution(self):
        return (len(self.getUnplacedBlocks()) == 0)

    def tunnelMacro(self, nMap, box, push):
        (px, py) = push
        (bx, by) = box

        if px != 0:
            # horizontal push
            while nMap[by+1][bx] == self.wall and nMap[by-1][bx] == self.wall:
                if nMap[by][bx+1] != self.space:
                    return None
                bx = bx + 1
        if py != 0:
            # vertical push
            while nMap[by][bx+1] == self.wall and nMap[by][bx-1] == self.wall:
                if nMap[by+1][bx] != self.space:
                    return None
                by = by + 1

        if (bx, by) != box:
            # Some puzzles have multiple tunnels and require a box to pushed
            # into the tunnel and then the player to travel through another
            # tunnel and push it out of the tunnel again - credit: AJ
            # To solve that, the macro will not push the box out of the tunnel
            # but rather leave it on the edge
            bx = bx - px
            by = by - py

            return (bx, by)

        return None

    def addMove(self, m):
        self.moveList.append(m)

    def setMoveList(self, l):
        self.moveList = deepcopy(l)

    def getMoveList(self):
        return self.moveList


    def move(self, nplayer):
        (x,y) = self.getPlayer()
        nMap = deepcopy(self.sm)
        box = None

        # Transform the current (past) location of the player

        if nMap[y][x] == self.player:
            nMap[y][x] = self.space
        elif nMap[y][x] == self.playerOnDeadlock:
            nMap[y][x] = self.deadlock
        else:
            nMap[y][x] = self.goal

        # transform the new location of the player

        (nx,ny) = nplayer
        xdiff = nx - x
        ydiff = ny - y
        m = (xdiff, ydiff)
        carry = False
        if nMap[ny][nx] == self.space:
            nMap[ny][nx] = self.player
        elif nMap[ny][nx] == self.goal:
            nMap[ny][nx] = self.playerOnGoal
        elif nMap[ny][nx] == self.deadlock:
            nMap[ny][nx] = self.playerOnDeadlock
        elif nMap[ny][nx] == self.block:
            carry = True
            nMap[ny][nx] = self.player
        else:
            carry = True
            nMap[ny][nx] = self.playerOnGoal

        # push a block into a new space if necessary
        if carry:
            bx = nx + xdiff
            by = ny + ydiff

            box = self.tunnelMacro(nMap, (bx, by), m)
            #box = None
            if box is not None:
                # print "TUNNEL"
                #  self.printMap()
                #  print "-------"
                # print "Tunnel From ", (bx, by), " to ", box
                (bx, by) = box

                if nMap[ny][nx] == self.player:
                    nMap[ny][nx] = self.space
                elif nMap[ny][nx] == self.playerOnDeadlock:
                    nMap[ny][nx] = self.deadlock
                elif nMap[ny][nx] == self.playerOnGoal:
                    nMap[ny][nx] = self.goal
                else:
                    print "WTF1=", nMap[ny][nx]

                nx = bx - xdiff
                ny = by - ydiff
                # it must be a space (that's checked inside tunnelMacro)

                nMap[ny][nx] = self.player

            # print ""
            # print bx,by
            # for line in nMap:
            #     print line

            # Place the box
            if nMap[by][bx] == self.space:
                nMap[by][bx] = self.block
            elif nMap[by][bx] == self.goal:
                nMap[by][bx] = self.blockOnGoal
            else:
                print "WTF2=", nMap[by][bx]


        nSokoMap = SokoMap()
        nSokoMap.setMap(nMap)
        nSokoMap.setMoveList(self.getMoveList())
        nSokoMap.addMove(m)

        # if box is not None:
        #     nSokoMap.printMap()
        return nSokoMap

    def _filter_neighbours(self, (x,y), offsets, filt):
        for (dx,dy) in offsets:
            nxy = (x+dx,y+dy)
            if (filt(nxy)):
                yield nxy

    def children(self):
        return [self.move(nxy) for nxy in self._filter_neighbours(self.getPlayer(), [(0,-1),(0,1),(-1,0),(1,0)], (lambda nxy: self.isLegal(nxy)))]

    def getNeighbors(self, node):
        def filt((nx,ny)):
            try:
                return ny >= 0 and nx >= 0 and self.sm[ny][nx] != self.wall
            except IndexError:
                return False

        return self._filter_neighbours(node, [(1,0),(-1,0),(0,1),(0,-1)], filt)

    def shortestPath(self, source, target):
        """Dijkstra's algorithm from the pseudocode in wikipedia"""
        dist = {}
        prev = {}
        q = []
        for y,a in enumerate(self.sm):
             for x,b in enumerate(self.sm[y]):
                 dist[(x,y)] = sys.maxint
                 prev[(x,y)] = None
                 q.append((x,y))
        dist[source] = 0

        while len(q) is not 0:
            # find the node with minimum value (u)
            d = deepcopy(dist)
            while True:
                b = dict(map(lambda item: (item[1],item[0]), d.items()))
                u = b[min(b.keys())]
                if u not in q:
                    d.pop(u)
                else:
                    break

            if dist[u] == sys.maxint: # remaining nodes are inaccessible
                break

            q.remove(u)


            if u == target: # target found
                break

            for v in self.getNeighbors(u):
                alt = dist[u] + 1
                if alt < dist[v]:
                    dist[v] = alt
                    prev[v] = u

        s = []
        u = target
        while prev[u] is not None:
            s.append(u)
            u = prev[u]
        s.reverse()

        return s


    def buildInfluenceTable(self):
        self.influenceTable = {}
        for sy,a in enumerate(self.sm):
            for sx,b in enumerate(self.sm[sy]):
                inf = {}
                if self.sm[sy][sx] == self.wall:
                    break
                for ty,a in enumerate(self.sm):
                    for tx,b in enumerate(self.sm[ty]):
                        if self.sm[ty][tx] == self.wall:
                            break
                        path = self.shortestPath((sx, sy), (tx, ty))
                        score = 0.0
                        for s in path:
                            (x, y) = s
                            sscore = 0.0
                            # Alternatives
                            for n in self.getNeighbors(s):
                                if n not in path:
                                    (nx, ny) = n
                                    px = nx - x
                                    py = ny - y
                                    hx = x - px
                                    hy = y - py
                                    if self.sm[ny][nx] == self.wall:
                                        sscore = 0
                                    elif self.sm[hy][hx] != self.wall:
                                        # "pushability" test
                                        # this tests if we can push a box from
                                        # s to n. It's an inacurate test
                                        # i.e. it's not always possible with
                                        # this condition but it will do
                                        sscore = 2
                                    else:
                                        sscore = 1
                            # Goal-Skew
                            for g in self.getGoals():
                                gpath = self.shortestPath((sx,sy), g)
                                if s in gpath:
                                    sscore = sscore / 2
                                    break

                            # Connection
                            si = path.index(s)
                            if len(path) < si+1:
                                n = path[si+1]
                                (nx, ny) = n
                                px = nx - x
                                py = ny - y
                                hx = x - px
                                hy = y - py
                                # Same poor test for "pushability" as before
                                if self.sm[hy][hx] != self.wall:
                                    sscore = sscore + 2
                                else:
                                    sscore = sscore + 1

                            # Tunnel
                            if si > 0:
                                (mx, my) = path[si-1]
                                px = x - mx
                                py = y - my

                                if px != 0: # horizontal push
                                    if self.sm[my+1][mx] == self.wall and \
                                       self.sm[my-1][mx] == self.wall:
                                        sscore = 0
                                else:   # vertical push
                                    if self.sm[my][mx+1] == self.wall and \
                                       self.sm[my][mx-1] == self.wall:
                                        sscore = 0

                            score = score + sscore
                        inf[(tx, ty)] = score
                self.influenceTable[(sx, sy)] = deepcopy(inf)

        average = 0.0
        count = 0

        for k,v in self.influenceTable:
            for kk, vv in v:
                count = count + 1
                average = average + vv

        average = average / count
        if average < 6:
            self.influenceThresh = 6
        else:
            self.influenceThresh = average

        self.influenceHistory = 10

    class DirectView:
        def __init__(self, sm):
            self.sm = sm

        def get(self, (y, x)):
            return self.sm[y][x]

        def set(self, (y, x), val):
            self.sm[y][x] = val
            return

        def y_len(self):
            return len(self.sm)

        def x_len(self):
            return max([row.len for row in self.sm])

    class Proxy_View:
        def __init__(self, v):
            self.v = v

        def _map(self, p):
            return p

        def get(self, p):
            return self.v.get(self._map(p))

        def set(self, p, val):
            return self.v.set(self._map(p), val)

        def y_len(self):
            return self.v.y_len()

        def x_len(self):
            return self.v.x_len()

    class Swap_XY_View(Proxy_View):
        def _map(self, (y, x)):
            return (x,y)

        def y_len(self):
            return self.v.x_len()

        def x_len(self):
            return self.v.y_len()

    def staticDeadlock(self):
        """Detects fixed deadlocks (very basic, not perfect"""

        def _place_deadlock(y,x,delta_y,delta_x):
            try:
                if self.sm[y+delta_y][x] == self.wall and \
                   self.sm[y][x+delta_x] == self.wall:
                    self.sm[y][x] = self.deadlock
                    return True
            except IndexError:
                pass
            return False

        # Place Deadlock Markers in corners (without goals)
        for y,a in enumerate(self.sm):
            for x,b in enumerate(self.sm[y]):
                if x == 0 or x == (len(self.sm[0])-1) or \
                   y == 0 or (y == len(self.sm)-1):
                    continue
                if self.sm[y][x] == self.space:
                    _place_deadlock(y,x,-1,-1) or \
                    _place_deadlock(y,x,-1,1) or \
                    _place_deadlock(y,x,1,-1) or \
                    _place_deadlock(y,x,1,1)

        # Connect Deadlock Markers if they next to a contin. wall w/o goals
        def connect_markers(dx,dy, view):
            up = True
            down = True
            found = False
            x = dx

            while x > 1:
                x = x - 1
                try:
                    if view.get((dy,x)) == self.deadlock:
                        found = True
                        break
                except IndexError:
                    break

            if found:
                sx = x
                while x != dx:
                    x = x + 1
                    try:
                        if view.get((dy+1,x)) != self.wall and down:
                            down = False
                    except IndexError:
                        down = False
                    try:
                        if view.get((dy-1,x)) != self.wall and up:
                            up = False
                    except IndexError:
                        up = False
                    try:
                        val = view.get((dy,x))
                        if val != self.space and \
                           val != self.player and \
                           val != self.deadlock:
                            up = down = False
                    except IndexError:
                        down = up = False

                if up or down:
                    x = sx
                    while x != dx:
                        val = view.get((dy,x))
                        if val == self.space:
                            view.set((dy,x), self.deadlock)
                        elif val == self.player:
                            view.set((dy,x), self.playerOnDeadlock)
                        x = x + 1

        xy_v = self.DirectView(self.sm)
        yx_v = self.Swap_XY_View(xy_v)
        for dead in self.getDeadlocks():
            (dx,dy) = dead
            connect_markers(dx, dy, xy_v)
            connect_markers(dy, dx, yx_v)

