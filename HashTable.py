import SokoMap


class HashTable:
    def __init__(self):
        self.table = []
    
    
    def checkAdd(self, sokomap):
        keyList = []
        keyList.extend(sokomap.getBlocks())
        keyList.extend(sokomap.getPlayer())
        key = str(keyList)
        if key in self.table:
            return True
        else:
            self.table.append(key)
            return False
        