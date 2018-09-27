
class Zoi:
    'Common base class for all ZOIS'

    def __init__(self, id, posX, posY, scenario):
        print ("Creating new ZOI...")
        self.id = id
        self.scenario = scenario
        self.x = 0
        self.y = 0
        self.content_list = []
        self.displayZoi()


    def displayZoi(self):
        print("ID : ", self.id,  ", POS X: ", self.x,  ", POS Y: ", self.y, ", Content list length: ", len(self.content_list))