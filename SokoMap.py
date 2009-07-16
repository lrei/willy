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
        if len(self.getUnplacedBlocks()) != 0:
            return False
        else:
            return True

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
            return (bx, by)
        
        return None

    
    def move(self, nplayer):
        (x,y) = self.getPlayer()
        nMap = deepcopy(self.sm)
        
        # Transform the current (past) location of the player
 
        if nMap[y][x] == self.player:
            nMap[y][x] = self.space
        elif nMap[y][x] == self.playerOnDeadlock:
            nMap[y][x] = self.deadlock
        else:
            nMap[y][x] = self.goal
        
        # transform the new location of the player
        
        (nx,ny) = nplayer
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
            xdiff = nx - x
            ydiff = ny - y
            bx = nx + xdiff
            by = ny + ydiff
			
            #box = self.tunnelMacro(nMap, (bx, by), (xdiff, ydiff))
            box = None
            if box is not None:
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
        
        return nSokoMap
    
    def children(self):
        childList = []
        player = self.getPlayer()
        
        # move up
        (x,y) = player
        y = y - 1
        nplayer = (x,y)
        if self.isLegal(nplayer):
            childList.append(self.move(nplayer))
        
        # move down
        (x,y) = player
        y = y + 1
        nplayer = (x,y)
        if self.isLegal(nplayer):
            childList.append(self.move(nplayer))
        
        # move left
        (x,y) = player
        x = x - 1
        nplayer = (x,y)
        if self.isLegal(nplayer):
            childList.append(self.move(nplayer))
            
        # move right
        (x,y) = player
        x = x + 1
        nplayer = (x,y)
        if self.isLegal(nplayer):
            childList.append(self.move(nplayer))

        return childList
    
    def staticDeadlock(self):
        """Detects fixed deadlocks (very basic, not perfect"""

		# Place Deadlock Markers in corners (without goals)
        for y,a in enumerate(self.sm):
            for x,b in enumerate(self.sm[y]):
                if x == 0 or x == (len(self.sm[0])-1) or \
				   y == 0 or (y == len(self.sm)-1):
                    continue
                if self.sm[y][x] == self.space:
                    try:
                        if self.sm[y-1][x] == self.wall and \
						   self.sm[y][x+1] == self.wall:
                            self.sm[y][x] = self.deadlock
                    except IndexError:
                        pass
                    try:
                        if self.sm[y+1][x] == self.wall and \
						   self.sm[y][x+1] == self.wall:
                            self.sm[y][x] = self.deadlock
                    except IndexError:
                        pass
                    try:
                        if self.sm[y-1][x] == self.wall and \
						   self.sm[y][x-1] == self.wall:
                            self.sm[y][x] = self.deadlock
                    except IndexError:
                        pass
                    try:
                        if self.sm[y+1][x] == self.wall and \
						   self.sm[y][x-1] == self.wall:
                            self.sm[y][x] = self.deadlock
                    except IndexError:
                        pass
        
        # Connect Deadlock Markers if they next to a contin. wall w/o goals
        for dead in self.getDeadlocks():
            (dx,dy) = dead
            up = True
            down = True
            found = False
            x = dx
            
            #print "Deadlock: ",dead
            ##################
            ### HORIZONTAL ###
            ##################
            while x > 1:
                x = x - 1
                if self.sm[dy][x] == self.deadlock:
                    found = True
                    break;
                
            if found:
                sx = x
                while x != dx:
                    x = x + 1
                    try:
                        if self.sm[dy+1][x] != self.wall and down:
                            down = False
                    except IndexError:
                        down = False
                    try:
                        if self.sm[dy-1][x] != self.wall and up:
                            up = False
                    except IndexError:
                        up = False
                    try:
                        if self.sm[dy][x] != self.space and \
                           self.sm[dy][x] != self.player and \
                           self.sm[dy][x] != self.deadlock:
                            up = down = False
                    except IndexError:
                        down = up = False
                
                if up or down:
                    x = sx
                    while x != dx:
                        if self.sm[dy][x] == self.space:
                            self.sm[dy][x] = self.deadlock
                        elif self.sm[dy][x] == self.player:
                            self.sm[dy][x] = self.playerOnDeadlock
                        x = x + 1
                
            ################
            ### VERTICAL ###
            ################
            (dx,dy) = dead
            up = True
            down = True
            found = False
            y = dy

            while y > 1:
                y = y - 1
                try:
                    if self.sm[y][dx] == self.deadlock:
                        found = True
                        break;
                except IndexError:
                    break;
                    
            if found:
                sy = y
                while y != dy:
                    y = y + 1
                    try:
                        if self.sm[y][dx+1] != self.wall and down:
                            down = False
                    except IndexError:
                        down = False
                    try:
                        if self.sm[y][dx-1] != self.wall and up:
                            up = False
                    except IndexError:
                        up = False
                    try:
                        if self.sm[y][dx] != self.space and \
                           self.sm[y][dx] != self.player and \
                           self.sm[y][dx] != self.deadlock:
                            up = down = False
                    except IndexError:
                        down = up = False
                           
                if up or down:
                    y = sy
                    while y != dy:
                        if self.sm[y][dx] == self.space:
                            self.sm[y][dx] = self.deadlock
                        elif self.sm[y][dx] == self.player:
                            self.sm[y][dx] = self.playerOnDeadlock
                        y = y + 1