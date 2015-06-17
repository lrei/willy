import SokoMap


class HashTable:
    def __init__(self):
        self.table = {}

    # sm is SokoMap
    def checkAdd(self, sm):
        key = str(sm.getBlocks() + [sm.getPlayer()])
        if key in self.table:
            return True
        else:
            self.table[key] = True
            return False

