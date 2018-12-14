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
        z=[]
        l = []
        ids = []
        zois = []
        for i in range(0,self.scenario.num_users):
            x.append(self.scenario.usr_list[i].x_list[-1])
            y.append(self.scenario.usr_list[i].y_list[-1])
            z.append(len(self.scenario.usr_list[i].messages_list))
            l.append(self.scenario.usr_list[i].zones.values())

            print("User id: ", self.scenario.usr_list[i].id, "position x: ", self.scenario.usr_list[i].x_list[-1] , "position y: ", self.scenario.usr_list[i].y_list[-1], "zones: ",self.scenario.usr_list[i].zones.values())

        # print(x)
        # print(y)
        file = open(str(self.uid) +'/userLastPosition-'+str(self.s)+'.txt', "w")
        file.write(json.dumps(x))
        file.write(json.dumps("&"))
        file.write(json.dumps(y))
        file.write(json.dumps("&"))
        file.write(json.dumps(z))
        file.write(json.dumps("&"))
        file.write(json.dumps(l))
        for h in self.scenario.zois_list:
            file.write(json.dumps("&"))
            file.write(json.dumps(h.x))
            file.write(json.dumps("&"))
            file.write(json.dumps(h.y))
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

    def statisticsList(self,slots, zoi_users, zoi, rep_users, rep, per_users, per,attempts):
         np.savetxt(str(self.uid)+'/dump-'+str(self.s)+'.txt', np.column_stack((slots, zoi_users, zoi, rep_users, rep, per_users, per,attempts)),
         fmt="%i %i %i %i %i %i %i %i")

    ####### Connection duration list

    def connectionDurationAndMore(self,contacts_per_slot_per_user):
        with open(str(self.uid)+'/contacts-per-slot-per-user-'+str(self.s)+'.json', 'w') as fp:
            json.dump(contacts_per_slot_per_user, fp)

        with open(str(self.uid)+'/connection-duration-list-'+str(self.s)+'.json', 'w') as fp2:
            json.dump(self.scenario.connection_duration_list, fp2)

    ####### Availability per zoi per slot

    def availabilityPerZoi(self,availability_per_zoi):
        f = open(str(self.uid)+'/availability-per-zoi-'+str(self.s)+'.txt',"w")
        f.write(str(availability_per_zoi))
        f.close()

     ####### Availability per content per slot

    def availabilityPerContent(self,a_per_content):
        with open(str(self.uid)+'/availability-per-content-'+str(self.s)+'.json', 'w') as fp:
            json.dump(a_per_content, fp)


    ####### Availability final point per simulation

    def availabilityPerSimulation(self,printa):
        f = open(str(self.uid)+'/availability_points-'+str(self.s)+'.txt',"w")
        f.write(str(printa))
        f.close()

    ####### list of availabilities per slot per simulation

    def listOfAveragesPerSlot(self,availabilities_list_per_slot):
        outfile = open(str(self.uid)+'/availability_per_slot_per_sim-'+str(self.s)+'.txt', 'w')
        for result in availabilities_list_per_slot:
            outfile.writelines(str(result))
            outfile.write('\n')
        outfile.close()

    ########### number of connections that started but didn't finish. With the same number of slots as hand shake + 1 slot to check 
    # that they don't have anything to exchange
    def con0exchange(self):
        f = open(str(self.uid)+'/counters-'+str(self.s)+'.txt',"w")
        f.write(str(self.scenario.count_0_exchange_conn)+"\n")
        f.write(str(self.scenario.count_non_useful)+"\n")
        f.write(str(self.scenario.count_useful)+"\n")
        f.close()
        