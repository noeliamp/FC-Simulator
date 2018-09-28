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

    def statisticsList(self,slots, zoi_users, zoi, rep_users, rep, per_users, per,failures, attempts):
         np.savetxt(str(self.uid)+'/dump-'+str(self.s)+'.txt', np.column_stack((slots, zoi_users, zoi, rep_users, rep, per_users, per,failures, attempts)),
         fmt="%i %i %i %i %i %i %i %i %i")

    ####### Connection duration list

    def connectionDurationAndMore(self,contacts_per_slot_per_user):
        connection_duration_list = []
        successes_list_A = []
        ex_list_A = []
        successes_list_B = []
        ex_list_B = []

        for k in range(0,self.scenario.num_users):
            connection_duration_list.append(self.scenario.usr_list[k].connection_duration_list)
            successes_list_A.append(self.scenario.usr_list[k].successes_list_A)
            ex_list_A.append(self.scenario.usr_list[k].ex_list_print_A)
            successes_list_B.append(self.scenario.usr_list[k].successes_list_B)
            ex_list_B.append(self.scenario.usr_list[k].ex_list_print_B)


        flat_list_con = [item for sublist in connection_duration_list for item in sublist]
        flat_list_suc_A = [item for sublist in successes_list_A for item in sublist]
        flat_list_exc_A = [item for sublist in ex_list_A for item in sublist]
        flat_list_suc_B = [item for sublist in successes_list_B for item in sublist]
        flat_list_exc_B = [item for sublist in ex_list_B for item in sublist]

        np.savetxt(str(self.uid)+'/connection-duration-list-'+str(self.s)+'.txt', flat_list_con , fmt="%i") 
        np.savetxt(str(self.uid)+'/successes-list-A-'+str(self.s)+'.txt', flat_list_suc_A , fmt="%i") 
        np.savetxt(str(self.uid)+'/exchange-list-A-'+str(self.s)+'.txt', flat_list_exc_A , fmt="%i") 
        np.savetxt(str(self.uid)+'/successes-list-B-'+str(self.s)+'.txt', flat_list_suc_B , fmt="%i") 
        np.savetxt(str(self.uid)+'/exchange-list-B-'+str(self.s)+'.txt', flat_list_exc_B , fmt="%i") 

        with open(str(self.uid)+'/contacts-per-slot-per-user-'+str(self.s)+'.json', 'w') as fp:
            json.dump(contacts_per_slot_per_user, fp)

    ####### Availability per zoi per slot

    def availabilityPerZoi(self,availability_per_zoi):
        f = open(str(self.uid)+'/availability-per-zoi-'+str(self.s)+'.txt',"w")
        f.write(str(availability_per_zoi))
        f.close()
