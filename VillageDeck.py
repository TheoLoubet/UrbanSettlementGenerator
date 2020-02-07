from random import shuffle

S = [4, 16] # deck size for villages sized 6x6 chunks or less
M = [9, 32] # deck size for villages sized in less than 9x9 chunks
L = [16, 64] # deck size for villages sized in less than 12x12 chunks
XL = [36, 256] # deck size for all the bigger sized villages

class VillageDeck:

    nbBuildings = nbHouses = nbFarms = nbWindmills = 0
    centerDeck = []
    suburbDeck = []

    def __init__(self, type, width, depth):

        def getSize(width, depth):
            size = 0
            area = width * depth
            if area < 10000:                        size = S
            elif area >= 10000 and area < 20000:    size = M
            elif area >= 20000 and area < 35000:    size = L
            else:                                   size = XL
            return size

        self.type = type
        self.size = getSize(width, depth)
        print("deck size : {}".format(self.size))
        self.setType()

    def setType(self):
        if self.type == "basic":    self.setBasicType(self.size)
        if self.type == "oneHouse": self.setOneHouseType(self.size)
        if self.type == "city": self.setCityType(self.size)

        self.printDeck()
        shuffle(self.centerDeck)
        shuffle(self.suburbDeck)
        self.printDeck()

    def setBasicType(self, size):
        for i in range(0, size[0]):
            self.centerDeck.append('h')
        for i in range(0, size[1]):
            self.suburbDeck.append('f')

    def setOneHouseType(self, size):
        self.centerDeck.append('h')
        for i in range(0, size[0] - 1):
            self.centerDeck.append('f')
        for i in range(0, size[1]):
            self.suburbDeck.append('f')

    def setCityType(self, size):
        for i in range(0, size[0]):
            self.centerDeck.append('b')
        for i in range(0, size[1] // 2):
            self.suburbDeck.append('h')
            self.suburbDeck.append('f')


    def printDeck(self):
        print("Buildings in center deck : ")
        print('[%s]' % ', '.join(map(str, self.centerDeck)))
        print("Buildings in suburb deck : ")
        print('[%s]' % ', '.join(map(str, self.suburbDeck)))

    def popCenterDeck(self):
        return self.centerDeck.pop()

    def popSuburbDeck(self):
        return self.suburbDeck.pop()

    def getCenterDeck(self):
        return self.centerDeck

    def getSuburbDeck(self):
        return self.suburbDeck
