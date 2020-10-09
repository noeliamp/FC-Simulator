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
        for i in self.scenario.usr_list:
            x.append(i.x_pos)
            y.append(i.y_pos)
            z.append(len(i.messages_list))
            # l.append(i.myFuture[len(i.myFuture)-1])


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
            file.write(json.dumps("u"))
            file.write(json.dumps("&"))
            file.write(json.dumps(self.scenario.radius_of_replication))
            file.write(json.dumps("&"))
            file.write(json.dumps(self.scenario.radius_of_replication))

        for i in self.scenario.usr_list:
            ids.append(i.id)

        for i in self.scenario.zois_list:
            zois.append(i.id)
        
        file.write(json.dumps("&"))
        file.write(json.dumps(ids))
        file.write(json.dumps("&"))
        file.write(json.dumps(zois))
        file.close()

    ####### Connection duration list

    def connectionDurationAndMore(self,contents_per_slot_per_user,rzs_per_slot_per_user,contact_mean,contact_len_mean,a_per_content_only_value,contacts_per_node):
        # with open('results/'+str(self.uid)+'/contacts-per-slot-per-user.json', 'w') as fp:
        #     json.dump(contacts_per_slot_per_user, fp)

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

        with open('results/'+str(self.uid)+'/contacts-per-node.json', 'w') as fp8:
            json.dump(contacts_per_node, fp8)


     ####### Availability per content per slot

    def availabilityPerContent(self,a_per_content):
        with open('results/'+str(self.uid)+'/availability-per-content.json', 'w') as fp:
            json.dump(a_per_content, fp)

    ####### Replicas per content per slot

    def replicasPerContent(self,replicas):
        with open('results/'+str(self.uid)+'/replicas-per-content.json', 'w') as fp:
            json.dump(replicas, fp)


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

    ####### Probabilities per user 
    def probabilities(self,probabilities):
        with open('results/'+str(self.uid)+'/probabilities.json', 'w') as fp:
            json.dump(probabilities, fp)
