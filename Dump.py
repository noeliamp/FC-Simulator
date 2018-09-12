from collections import OrderedDict
import json

###################### DATA DUMP  ################################################
class Dump:
    'Common base class for all dumps'

    def __init__(self,scenario):
        self.id = 1
        self.scenario= scenario

    ####### last user's position
    def userLastPosition(self,uid):
        x = []
        y = []
        ids = []
        zois = []
        for i in range(0,self.scenario.num_users):
            x.append(self.scenario.usr_list[i].x_list[-1])
            y.append(self.scenario.usr_list[i].y_list[-1])
            print("User id: ", self.scenario.usr_list[i].id, "position x: ", self.scenario.usr_list[i].x_list[-1] , "position y: ", self.scenario.usr_list[i].y_list[-1])

        # print(x)
        # print(y)
        file = open(str(uid) +'/userLastPosition.txt', "w")
        file.write(json.dumps(x))
        file.write(json.dumps("&"))
        file.write(json.dumps(y))
        for z in self.scenario.zois_list:
            file.write(json.dumps("&"))
            file.write(json.dumps(z.x))
            file.write(json.dumps("&"))
            file.write(json.dumps(z.y))
            file.write(json.dumps("&"))
            file.write(json.dumps(self.scenario.radius_of_interest))
            file.write(json.dumps("&"))
            file.write(json.dumps(self.scenario.radius_of_replication))
            file.write(json.dumps("&"))
            file.write(json.dumps(self.scenario.radius_of_persistence))

        for i in range(0,self.scenario.num_users):
            ids.append(self.scenario.usr_list[i].id)

        for i in self.scenario.zois_list:
            zois.append(i.id)
        
        file.write(json.dumps("&"))
        file.write(json.dumps(ids))
        file.write(json.dumps("&"))
        file.write(json.dumps(zois))
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

        for i in self.scenario.usr_list:
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


