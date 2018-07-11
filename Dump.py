from collections import OrderedDict
import json

###################### DATA DUMP  ################################################
class Dump:
    'Common base class for all dumps'

    def __init__(self,scenario):
        self.id = 1
        self.scenario= scenario

    ####### last user's position
    def userLastPosition(self):
        x = []
        y = []
        for i in range(0,self.scenario.num_users):
            x.append(self.scenario.usrList[i].x_list[-1])
            y.append(self.scenario.usrList[i].y_list[-1])

        # print(x)
        # print(y)
        file = open("userLastPosition.txt", "w")
        file.write(json.dumps(x))
        file.write(json.dumps("&"))
        file.write(json.dumps(y))
        file.close()

    ####### how many nodes have the contents in each zone 

    def infoPerZone(self):
        interest = OrderedDict()
        replication = OrderedDict()
        persistence = OrderedDict()
        outer = OrderedDict()

        interest["interest"]=OrderedDict()
        replication["replication"]=OrderedDict()
        persistence["persistence"]= OrderedDict()
        outer["outer"] = OrderedDict()      

        for i in self.scenario.usrList:
            if i.zone == "interest":
                interest["interest"][i.id] = len(i.messages_list)
            if i.zone == "replication":
                replication["replication"][i.id] = len(i.messages_list)
            if i.zone == "persistence":
                persistence["persistence"][i.id] = len(i.messages_list)
            if i.zone == "outer":
                outer["outer"][i.id] = len(i.messages_list)

        with open('infoPerZone.txt', 'w') as file:
            file.write(json.dumps(interest))
            file.write(json.dumps(replication))
            file.write(json.dumps(persistence))
            file.write(json.dumps(outer))

        file.close()


