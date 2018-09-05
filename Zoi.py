import numpy as np

class Zoi:
    'Common base class for all ZOIS'

    def __init__(self, id,scenario):
        # print ("Creating new ZOI...")
        self.id = id
        self.scenario = scenario
        self.radius_of_persistence = self.scenario.radius_of_persistence
        self.radius_of_replication = self.scenario.radius_of_replication
        self.radius_of_interest = self.scenario.radius_of_interest
        self.x = np.random.uniform(-self.scenario.max_area + self.radius_of_persistence, self.scenario.max_area - self.radius_of_persistence)
        self.y = np.random.uniform(-self.scenario.max_area + self.radius_of_persistence, self.scenario.max_area - self.radius_of_persistence)
        self.content_list = []
        # self.displayMessage()


    def displayZOI(self):
        print("ID : ", self.id,  ", Radius: ", self.radius_of_persistence,  ", X: ", self.x,  ", Y: ", self.y,  ", Content list length: ", len(self.content_list))