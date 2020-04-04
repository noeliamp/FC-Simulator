from collections import OrderedDict
import json
import numpy as np


###################### DATA DUMP  ################################################
class Dump:
    'Common base class for all dumps'

    def __init__(self,scenario,uid):
        self.id = 1
        self.scenario= scenario
        self.uid = uid 

    ####### last user's position
    def userLastPosition(self):
        x = []
        y = []
        z=[]
        l = []
        ids = []
        zois = []
        print(self.scenario.num_users)
        for i in range(0,self.scenario.num_users):
            x.append(self.scenario.usr_list[i].x_list[-1])
            y.append(self.scenario.usr_list[i].y_list[-1])
            z.append(len(self.scenario.usr_list[i].messages_list))
            print(self.scenario.usr_list[i].myFuture)
            l.append(self.scenario.usr_list[i].myFuture[len(self.scenario.usr_list[i].myFuture)-1])

            # print("User id: ", self.scenario.usr_list[i].id, "position x: ", self.scenario.usr_list[i].x_list[-1] , "position y: ", self.scenario.usr_list[i].y_list[-1], "zones: ",self.scenario.usr_list[i].zones.values())

        # print(x)
        # print(y)
        file = open('results/'+str(self.uid) +'/userLastPosition.txt', "w")
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
            file.write(json.dumps(self.scenario.radius_of_replication))

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
         np.savetxt('results/'+str(self.uid)+'/dump.txt', np.column_stack((slots, zoi_users, zoi, rep_users, rep, per_users, per,attempts)),
         fmt="%i %i %i %i %i %i %i %i")

    ####### Connection duration list

    def connectionDurationAndMore(self,contacts_per_slot_per_user,contents_per_slot_per_user,rzs_per_slot_per_user,contact_mean,contact_len_mean,a_per_content_only_value):
        with open('results/'+str(self.uid)+'/contacts-per-slot-per-user.json', 'w') as fp:
            json.dump(contacts_per_slot_per_user, fp)

        with open('results/'+str(self.uid)+'/rzs-per-slot-per-user.json', 'w') as fp:
            json.dump(rzs_per_slot_per_user, fp)

        with open('results/'+str(self.uid)+'/connection-duration-list.json', 'w') as fp2:
            json.dump(self.scenario.connection_duration_list, fp2)

        with open('results/'+str(self.uid)+'/contents-list.json', 'w') as fp3:
            json.dump(contents_per_slot_per_user, fp3)

        with open('results/'+str(self.uid)+'/connection-location-list.json', 'w') as fp4:
            json.dump(self.scenario.connection_location_list, fp4)

        with open('results/'+str(self.uid)+'/contacts-mean.json', 'w') as fp5:
            json.dump(contact_mean, fp5)

        with open('results/'+str(self.uid)+'/contacts-mean-length.json', 'w') as fp6:
            json.dump(contact_len_mean, fp6)

        with open('results/'+str(self.uid)+'/a-per-content-only-value.json', 'w') as fp7:
            json.dump(a_per_content_only_value, fp7)

    ####### Availability per zoi per slot

    def availabilityPerZoi(self,availability_per_zoi):
        f = open('results/'+str(self.uid)+'/availability-per-zoi.txt',"w")
        f.write(str(availability_per_zoi))
        f.close()

     ####### Availability per content per slot

    def availabilityPerContent(self,a_per_content):
        with open('results/'+str(self.uid)+'/availability-per-content.json', 'w') as fp:
            json.dump(a_per_content, fp)

    ####### Replicas per content per slot

    def replicasPerContent(self,replicas):
        with open('results/'+str(self.uid)+'/replicas-per-content.json', 'w') as fp:
            json.dump(replicas, fp)


    ####### Availability final point per simulation

    def availabilityPerSimulation(self,printa):
        f = open('results/'+str(self.uid)+'/availability_points.txt',"w")
        f.write(str(printa))
        f.close()

    ####### list of availabilities per slot per simulation

    def listOfAveragesPerSlot(self,availabilities_list_per_slot):
        outfile = open('results/'+str(self.uid)+'/availability_per_slot_per_sim.txt', 'w')
        for result in availabilities_list_per_slot:
            outfile.writelines(str(result))
            outfile.write('\n')
        outfile.close()

    ########### number of connections that started but didn't finish. With the same number of slots as hand shake + 1 slot to check 
    # that they don't have anything to exchange
    def con0exchange(self):
        f = open('results/'+str(self.uid)+'/counters.txt',"w")
        f.write(str(self.scenario.count_0_exchange_conn)+"\n")
        f.write(str(self.scenario.count_non_useful)+"\n")
        f.write(str(self.scenario.count_useful)+"\n")
        f.close()
        

    ####### Number of users in the ZOI per slot

    def nodesZoiPerSlot(self,nodes_in_zoi):
        with open('results/'+str(self.uid)+'/nodes-in-zoi.json', 'w') as fp:
            json.dump(nodes_in_zoi, fp)


    ####### Path followed by every node

    def nodesPath(self):
        outfile = open('results/'+str(self.uid)+'/nodes-path.txt', 'w')
        for n in self.scenario.usr_list:
            outfile.writelines(str(n.id)+"\n")
            outfile.writelines(str(n.x_list)+"\n")
            outfile.writelines(str(n.y_list)+"\n")
        outfile.close()


    ####### how long are nodes inside RZs

    def nodesInRz(self):
        outfile = open('results/'+str(self.uid)+'/nodes-rz-IO.txt', 'w')
        for n in self.scenario.usr_list:
            outfile.writelines(str(n.list_of_zois_future) + "\n")
        outfile.close()
        outfile = open('results/'+str(self.uid)+'/nodes-rz.txt', 'w')
        for n in self.scenario.usr_list:
            outfile.writelines(str(n.myFuture.values()) + "\n")
        outfile.close()


        