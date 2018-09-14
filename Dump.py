from collections import OrderedDict
import json
import numpy as np


###################### DATA DUMP  ################################################
class Dump:
    'Common base class for all dumps'

    def __init__(self,scenario,uid,s):
        self.id = 1
        self.scenario= scenario
        self.uid = uid 
        self.s = s

    ####### last user's position
    def userLastPosition(self):
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
        file = open(str(self.uid) +'/userLastPosition-'+str(self.s)+'.txt', "w")
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

    ####### Lists for statistics 

    def statisticsList(self,slots, zoi_users, zoi, rep_users, rep, per_users, per,failures, attempts):
         np.savetxt(str(self.uid)+'/dump-'+str(self.s)+'.txt', np.column_stack((slots, zoi_users, zoi, rep_users, rep, per_users, per,failures, attempts)), 
         fmt="%i %i %i %i %i %i %i %i %i")

    ####### Connection duration list

    def connectionDuration(self):
        for k in range(0,self.scenario.num_users):
            connection_duration_list.append(self.scenario.usr_list[k].connection_duration_list)

        flat_list = [item for sublist in connection_duration_list for item in sublist]
        np.savetxt(str(self.uid)+'/connection-duration-list-'+str(self.s)+'.txt', flat_list , fmt="%i") 


