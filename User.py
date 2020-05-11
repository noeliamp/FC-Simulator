from __future__ import division
import numpy as np
import math 
from collections import Counter 
from collections import OrderedDict
import sys
import geopy.distance

class User:
    'Common base class for all users'

    def __init__(self, id, posX, posY, scenario, max_memory,max_time_elapsed):

        # print ("Creating new user...")
        self.id = id
        self.scenario = scenario
        self.total_memory = max_memory
        self.messages_list = []
        self.exchange_list = []
        self.exchange_size = 0
        self.prev_peer = None
        self.busy = False 
        self.ongoing_conn = False
        self.db_exchange = False
        self.x_pos = posX
        self.y_pos= posY
        self.counter_list = []
        self.exchange_counter = 0
        self.used_memory = 0
        self.time_elapsed = OrderedDict()
        self.time_elapsed[0] = 0
        self.time_elapsed[1] = 0
        self.connection_duration = 0
        self.max_time_elapsed = max_time_elapsed
        self.myFuture = OrderedDict()
        # self.contacts_per_slot = OrderedDict()
        self.current_contacts = []
        self.contacts_frequency_list = [0]* self.scenario.num_users
        self.cross = False
        self.history = OrderedDict()
        self.rz_visits_info = []
        self.dicc_peers = OrderedDict()
        # self.prev_contact_mean = OrderedDict()
        # self.prev_contact_len_mean = OrderedDict()
        # self.final_stat = 1
        # self.contacts_count = OrderedDict()
        self.self_interests = [np.random.randint(0, 9) for p in range(0, np.random.randint(0, 9))]
        self.self_relations = [np.random.randint(0, self.scenario.num_users) for p in range(0, np.random.randint(0,self.scenario.num_users))]
        self.contacts_interests = [0]*10
        self.contacts_relations = [0]*self.scenario.num_users
        self.simPro = 0
        self.simInt = 0
        self.simSoc = 0
        self.simPIS = 0
        self.ego = np.zeros((self.scenario.num_users, self.scenario.num_users))
        self.ego_dict = OrderedDict()
        self.current_zoi = 99
        # self.displayUser()

    def displayUser(self):
        print("ID : ", self.id,  ", Total Memory: ", self.total_memory,  ", Used Memory: ", self.used_memory, ", PosX: ",self.x_pos, 
              ", PosY: ", self.y_pos, ", Is Paused: ", self.isPaused, ", Slots Paused: ", self.pause_slots, 
              ", Counter Paused: ", self.pause_counter, ", slot n: ", self.n, ", Message list: " , len(self.messages_list))

    def checkDB(self,z,c):
        for m in z.content_list:
            if m in self.messages_list:
                if z.id in self.time_elapsed:
                    if self.time_elapsed[z.id] == self.max_time_elapsed:
                        self.messages_list.remove(m)
                        self.used_memory =- m.size
                        self.exchange_size =- m.size
                        self.time_elapsed[z.id] = 0
                    else:
                        self.time_elapsed[z.id] += 1
                else:
                    self.time_elapsed[z.id] = 0

    def checkHistory(self,c):
        for k,v in self.history.items():
            if (c-v) >= self.max_time_elapsed:
                del self.history[k]

    # if within the time elpased the node is visiting a different zone, then the content is exchanged to bring it to the other side
    def crossing(self,c):
        self.cross = False
        for i in range(c,(c+self.max_time_elapsed)):
            if i < self.scenario.num_slots:
                if self.myFuture[i] != self.myFuture[c] and self.myFuture[i] != -1:
                    self.cross = True
                    break
        return self.cross
            

    def predict(self,nslots):
        self.list_of_zois_future = []
        for c in range(nslots):
            if c in self.scenario.long_tracesDic[self.id]:
                items = self.scenario.long_tracesDic[self.id][c]
                x = items[0]
                y = items[1]
                for z in self.scenario.zois_list:
                    if self.scenario.city =="Paderborn" or self.scenario.city =="Luxembourg":
                        d = np.power(x - z.x,2) + np.power(y - z.y,2)
                        if d < z.scenario.square_radius_of_replication:
                            self.myFuture[c] = z.id
                        if d > z.scenario.square_radius_of_replication:
                            if c not in self.myFuture:
                                self.myFuture[c] = -1 



                    if self.scenario.city !="Paderborn" and self.scenario.city !="Luxembourg":
                        coords_1 = (z.x, z.y)
                        coords_2 = (x, y)
                        d = geopy.distance.distance(coords_1, coords_2).m
                        if d < z.scenario.radius_of_replication:
                            self.myFuture[c] = z.id
                        if d > z.scenario.radius_of_replication:
                            if c not in self.myFuture:
                                self.myFuture[c] = -1 

            else:
                if c == 0:
                    # print(self.id,self.scenario.tracesDic[self.id].keys()[0])
                    first_c = list(self.scenario.long_tracesDic[self.id].keys())[0]
                    items = self.scenario.long_tracesDic[self.id][first_c]

                    x = items[0]
                    y = items[1]
                    for z in self.scenario.zois_list:
                        if self.scenario.city =="Paderborn" or self.scenario.city =="Luxembourg":
                            d = np.power(x - z.x,2) + np.power(y - z.y,2)
                        if self.scenario.city !="Paderborn" and self.scenario.city !="Luxembourg":
                            coords_1 = (z.x, z.y)
                            coords_2 = (x, y)
                            d = geopy.distance.distance(coords_1, coords_2).m
                        if d < z.scenario.square_radius_of_replication:
                            self.myFuture[c] = z.id
                        if d > z.scenario.square_radius_of_replication:
                            if c not in self.myFuture:
                                self.myFuture[c] = -1 
                else:
                    self.myFuture[c] = self.myFuture[c-1]
                
        # print(self.id, 'My future: ', self.myFuture.values()) 
        # self.rz_visits_info.append(self.myFuture[0])
 
        self.list_of_zois_future.append(99)
        for v in self.myFuture.values():
            if self.list_of_zois_future[-1] != v:
                self.list_of_zois_future.append(v)     

        # print(self.list_of_zois_future)  
        self.current_zoi = self.myFuture[c]

    # Method to read from the traces (stored in the scenario) each node's new position
    # This method will make a node move in every new slot to the next point in the list
    def readTraces(self,c):
        if c in self.scenario.tracesDic[self.id]:
            items = self.scenario.tracesDic[self.id][c]
            x = items[0]
            y = items[1]

            # print("Next point: ", x, y)   
            self.x_pos = x
            self.y_pos = y


    def getContacts(self,c):
         # print ("First -- My id is ", self.id, " Am I busy for this slot: ", self.busy)
        # add my current RZ to the list
        self.rz_visits_info.append(self.myFuture[c])
        self.current_contacts = []

        # Include the neighbours found in this slot for contacts statistics
        for user in self.scenario.usr_list:
            if user.id != self.id:
                if self.scenario.city =="Paderborn" or self.scenario.city =="Luxembourg":
                    pos_user = np.power(user.x_pos-self.x_pos,2) + np.power(user.y_pos-self.y_pos,2)
                if self.scenario.city != "Paderborn" and self.scenario.city !="Luxembourg":
                    coords_1 = (user.x_pos, user.y_pos)
                    coords_2 = (self.x_pos, self.y_pos)
                    pos_user = geopy.distance.distance(coords_1, coords_2).m
                    # print("Distancia---->",pos_user)
                # check if user is neighbour
                if pos_user < self.scenario.square_radius_of_tx:
                    # self.contacts_per_slot[c].append(user.id)
                    self.current_contacts.append(user.id)
                    self.contacts_frequency_list[user.id] = (self.contacts_frequency_list[user.id]+1)/(c+1)
                    if user.id not in self.dicc_peers.keys():
                        self.dicc_peers[user.id]= []
                        self.dicc_peers[user.id].append(c)
                    else:
                        self.dicc_peers[user.id].append(c)

                if pos_user > self.scenario.square_radius_of_tx:
                    self.contacts_frequency_list[user.id] = (self.contacts_frequency_list[user.id]+0)/(c+1)

                # count contact length when the contact is over with that user
                if user.id in self.dicc_peers and c != 0:
                    if c < self.scenario.num_slots-1 and c == self.dicc_peers[user.id][-1]+1:
                        ind = -1
                        coun = 0
                        if -ind == len(self.dicc_peers[user.id]):
                                coun = coun + 1
                        else:
                            while self.dicc_peers[user.id][ind] == self.dicc_peers[user.id][ind-1]+1:
                                ind = ind - 1 
                                coun = coun + 1
                                if -ind == len(self.dicc_peers[user.id]):
                                    coun = coun + 1
                                    break
                                if self.dicc_peers[user.id][ind] != self.dicc_peers[user.id][ind-1]+1:
                                    coun = coun + 1
                                    break

                        previous_zoi = self.myFuture[c-1]
                        if previous_zoi in self.scenario.prev_contact_len_mean:
                            self.scenario.prev_contact_len_mean[previous_zoi] = ((self.scenario.contacts_count[previous_zoi]*self.scenario.prev_contact_len_mean[previous_zoi]) + coun)/(self.scenario.contacts_count[previous_zoi]+1)
                            self.scenario.contacts_count[previous_zoi] = self.scenario.contacts_count[previous_zoi] + 1

                        if previous_zoi not in self.scenario.prev_contact_len_mean:
                            self.scenario.prev_contact_len_mean[previous_zoi] = coun
                            self.scenario.contacts_count[previous_zoi] = 1

                    if c == self.scenario.num_slots-1 and c == self.dicc_peers[user.id][-1]:
                        ind = -1
                        coun = 0
                        if len(self.dicc_peers[user.id])>1:
                            while self.dicc_peers[user.id][ind] == self.dicc_peers[user.id][ind-1]+1:
                                ind = ind - 1 
                                coun = coun + 1
                                if -ind == len(self.dicc_peers[user.id]):
                                    coun = coun + 1
                                    break
                        
                        if self.current_zoi in self.scenario.prev_contact_len_mean:
                            self.scenario.prev_contact_len_mean[self.current_zoi] = ((self.scenario.contacts_count[self.current_zoi]*self.scenario.prev_contact_len_mean[self.current_zoi]) + coun)/(self.scenario.contacts_count[self.current_zoi]+1)
                            self.scenario.contacts_count[self.current_zoi] = self.scenario.contacts_count[self.current_zoi] + 1
                          

                        if self.current_zoi not in self.scenario.prev_contact_len_mean:
                            self.scenario.prev_contact_len_mean[self.current_zoi] = coun
                            self.scenario.contacts_count[self.current_zoi] = 1
                       
    def computeStatistics(self,c):                         
        # statistics for decision making
        # computing the mean number of contacts
        # num_contacts = len(self.contacts_per_slot[c])
        num_contacts = len(self.current_contacts)

        if c == 0:
            self.scenario.prev_contact_mean[self.current_zoi] = num_contacts
            self.scenario.prev_contact_len_mean[self.current_zoi] = 0
            self.scenario.contacts_count[self.current_zoi] = 0
        else:
            if self.current_zoi not in self.scenario.prev_contact_mean:
                self.scenario.prev_contact_mean[self.current_zoi] = num_contacts
            else:
                indexes = [i for i, n in enumerate(self.rz_visits_info) if n == self.current_zoi]
                index = indexes.index(len(self.rz_visits_info)-1)
                self.scenario.prev_contact_mean[self.current_zoi] = ((index*self.scenario.prev_contact_mean[self.current_zoi])+num_contacts)/(index+1)
                    

        # computing the minimum from mean
        if self.scenario.prev_contact_mean[self.current_zoi] == 0:
            min_stats_mean = 1
        else:
            min_stats_mean = min(1,1/self.scenario.prev_contact_mean[self.current_zoi])

        # computing the minimum from len_mean
        if self.current_zoi not in self.scenario.prev_contact_len_mean:
            min_stats_len_mean = 1
        else:
            if self.scenario.prev_contact_len_mean[self.current_zoi] == 0:
                min_stats_len_mean = 1
            else:
                min_stats_len_mean = min(1,1/self.scenario.prev_contact_len_mean[self.current_zoi])


        ### final mean
        self.scenario.final_stat = (min_stats_mean+min_stats_len_mean)/2
        
    # method to allow nodes to exchange within a RZ and in the surroundings taking into account a maximum elapse time
    def userContactOutIn(self,c):
        if self.busy == False:
            # Once we have the list of neighbours, first check if there is a previous connection ongoing and the peer is still inside my tx range
            # which is the same as being in the neighbours list since we checked the positions above
            # if self.ongoing_conn == True and self.prev_peer in self.contacts_per_slot[c]:
            if self.ongoing_conn == True and self.prev_peer in self.current_contacts:

                self.connection_duration += 1
                self.prev_peer.connection_duration += 1
                # keep exchanging
                self.exchangeData(self.prev_peer,c)

            # else exchange data with a channel rate per slot
            else:
                # if my prev peer is not in my communication range we don't exchange data anymore
                # if self.ongoing_conn == True and self.prev_peer not in self.contacts_per_slot[c]:
                if self.ongoing_conn == True and self.prev_peer not in self.current_contacts:

                    if self.connection_duration not in self.scenario.connection_duration_list.keys():
                        self.scenario.connection_duration_list[self.connection_duration] = 1
                    else:
                        self.scenario.connection_duration_list[self.connection_duration] +=1

                    # Add the location of the connection
                    if self.current_zoi not in self.scenario.connection_location_list:
                        self.scenario.connection_location_list[self.current_zoi] = 1
                    else:
                        self.scenario.connection_location_list[self.current_zoi] +=1

                    # reset all parameters to start clean with a new peer
                    self.connection_duration = 0
                    self.prev_peer.connection_duration = 0
                    self.exchange_list = []
                    self.prev_peer.exchange_list = []
                    self.ongoing_conn = False
                    self.prev_peer.ongoing_conn = False
                

                # Continue looking for neighbours   
                # In case we want to connect with more than one neighbour we need to run a loop. Now we only select one neighbour from the list.
                if self.scenario.final_stat > 0.2:
                    neighbour = None
                    # for neigid in self.contacts_per_slot[c]:
                    for neigid in self.current_contacts:

                        for n in self.scenario.usr_list:
                            if n.id == neigid:
                                neig = n
                        if not neig.busy and neig.ongoing_conn == False:
                            neighbour = neig
                            break
                    if neighbour != None:
                        # Once we have a new neighbour chosen, we start exchanging, with PIS only if condition is True
                        if self.scenario.algorithm == "PIS":
                            self.PIS(neighbour) 
                        if self.scenario.algorithm != "PIS" or (self.simPIS + self.scenario.gamma) > 0:
                            self.scenario.attempts +=1
                            self.connection_duration += 1
                            neighbour.connection_duration +=  1
                            self.exchange_list = []
                            neighbour.exchange_list = []
                            # First, check the messages missing in the peers devices and add them to the exchange list of messages of every peer
                            for m in self.messages_list:
                                if m not in neighbour.messages_list: 
                                    self.exchange_list.append(m)
                                   
                            # After choosing the messages that are missing in the peer, we need to shuffle the list
                            np.random.shuffle(self.exchange_list)
                            for m in neighbour.messages_list:
                                if m not in self.messages_list:
                                    neighbour.exchange_list.append(m)
                                    
                            # After choosing the messages that are missing in the peer, we need to shuffle the list
                            np.random.shuffle(neighbour.exchange_list)
                            # Second, exchange the data with peer!! 
                            self.exchangeData(neighbour,c)

                      

    # method to allow nodes to exchange within a RZ
    def userContact(self,c):
        if self.busy == False:
            # Once we have the list of neighbours, first check if there is a previous connection ongoing and the peer is still inside my tx range
            # which is the same as been in the neighbours list since we checked the positions above
            # if self.ongoing_conn == True and self.prev_peer in self.contacts_per_slot[c]:
            if self.ongoing_conn == True and self.prev_peer in self.current_contacts:

                self.connection_duration += 1
                self.prev_peer.connection_duration += 1
                # keep exchanging 
                self.exchangeData(self.prev_peer,c)

            # else exchange data with a probability and within a channel rate per slot
            else:
                # if my prev peer is not in my communication range we don't exchange data anymore
                # if self.ongoing_conn == True and self.prev_peer not in self.contacts_per_slot[c]:
                if self.ongoing_conn == True and self.prev_peer not in self.current_contacts:

                    if self.connection_duration not in self.scenario.connection_duration_list.keys():
                        self.scenario.connection_duration_list[self.connection_duration] = 1
                    else:
                        self.scenario.connection_duration_list[self.connection_duration] +=1

                    # Add the location of the connection
                    if self.current_zoi not in self.scenario.connection_location_list:
                        self.scenario.connection_location_list[self.current_zoi] = 1
                    else:
                        self.scenario.connection_location_list[self.current_zoi] +=1

                    # reset all parameters to start clean with a new peer
                    self.connection_duration = 0
                    self.prev_peer.connection_duration = 0
                    self.exchange_list = []
                    self.prev_peer.exchange_list = []
                    self.ongoing_conn = False
                    self.prev_peer.ongoing_conn = False

                # Continue looking for neighbours   
                # In case we want to connect with more than one neighbour we need to run a loop. Now we only select one neighbour from the list.
                neighbour = None
                # for neig in self.contacts_per_slot[c]:
                for neig in self.current_contacts:

                        if not neig.busy and neig.ongoing_conn == False:
                            neighbour = neig
                            # print("I found a peer not busy and without ongoing connection. ", neighbour.id)
                            break
                if neighbour != None:
                    self.scenario.attempts +=1
                    # print("Attempts--- ", self.scenario.attempts)
                    self.connection_duration += 1
                    neighbour.connection_duration +=  1
                    self.exchange_list = []
                    neighbour.exchange_list = []
                    # First, check the messages missing in the peers devices and add them to the exchange list of messages of every peer
                    for m in self.messages_list:
                        if m not in neighbour.messages_list: # and m.zoi in neighbour.zones.keys(): # Does not work for connected zois
                            self.exchange_list.append(m)
                           

                    # After choosing the messages that are missing in the peer, we need to shuffle the list
                    np.random.shuffle(self.exchange_list)
                    for m in neighbour.messages_list:
                        if m not in self.messages_list:
                            neighbour.exchange_list.append(m)

                    # After choosing the messages that are missing in the peer, we need to shuffle the list
                    np.random.shuffle(neighbour.exchange_list)
                    # Second, exchange the data with peer!!
                    self.exchangeData(neighbour,c)
                        


    def socialFactorsUpdating(self,c):
        # for ide in self.contacts_per_slot[c]:
        for ide in self.current_contacts:
            for peerScn in self.scenario.usr_list:
                if peerScn.id == ide:
                    peer = peerScn
            # Physical Proximity Updating
            # for peerContact in peer.contacts_per_slot[c]:
            for peerContact in peer.current_contacts:

                self.ego[peer.id][peerContact] = peer.contacts_frequency_list[peerContact]
                self.ego[peerContact][peer.id] = peer.contacts_frequency_list[peerContact]
            # Interest Updating
            for iCont in range(len(self.contacts_interests)):
                if iCont in peer.self_interests:
                    self.contacts_interests[iCont] += (self.contacts_interests[iCont] + 1)/(c+1)
                else:
                    self.contacts_interests[iCont] += (self.contacts_interests[iCont] + 0)/(c+1)
            # Social Relationship Updating
            for rCont in range(len(self.contacts_relations)):
                if rCont in peer.self_relations:
                    self.contacts_relations[rCont] = (self.contacts_relations[rCont] + 1)/(c+1)
                else:
                    self.contacts_relations[rCont] = (self.contacts_relations[rCont] + 0)/(c+1)

    def similaritiesCalculation(self,c):
        if len(self.scenario.usr_list)>1:
            for destination in self.scenario.usr_list:
                if destination != self:
                    sum_pro = 0
                    sum_int = 0
                    sum_soc = 0
                    simpro = 0
                    simint = 0
                    simsoc = 0
                    simPro = []
                    simInt = []
                    simSoc = []
                    # for cSelf in self.contacts_per_slot[c]:
                    for cSelf in self.current_contacts:

                        # if cSelf in destination.contacts_per_slot[c]:
                        if cSelf in destination.current_contacts:

                            self.ego[cSelf][destination.id] 
                                
                    for iDest in destination.self_interests:
                        sum_int += self.contacts_interests[iDest]
                    
                    for rDest in destination.self_relations:
                        sum_soc += self.contacts_relations[rDest]


                    simpro = sum_pro * self.scenario.beta
                    simint = sum_int * self.scenario.beta
                    simsoc = sum_soc * self.scenario.beta
                    simPro.append(simpro)
                    simInt.append(simint)
                    simSoc.append(simsoc)

        
            self.simPro = np.average(simPro)
            self.simInt = np.average(simInt)
            self.simSoc = np.average(simSoc)        
    

    def PIS(self,peer):
        simDevPro = 0
        if self.simPro+peer.simPro != 0:
            simDevPro = (peer.simPro-self.simPro)/(self.simPro+peer.simPro)
        # print("simDevPro",simDevPro)
        simDevInt = 0
        if self.simInt+peer.simInt != 0:
            simDevInt = (peer.simInt-self.simInt)/(self.simInt+peer.simInt)
        # print("simDevInt",simDevInt)
        simDevSoc = 0
        if self.simSoc+peer.simSoc != 0:
            simDevSoc = (peer.simSoc-self.simSoc)/(self.simSoc+peer.simSoc)
        # print("simDevSoc",simDevSoc)
        self.simPIS = (self.scenario.rho*simDevPro)+(self.scenario.sigma*simDevInt)+(self.scenario.tau*simDevSoc)
        # print("simPIS",self.simPIS)

    # Method to check which DB is smaller and start exchanging it. 
    # At this point We have the messages to be exchange (exchange_list) and the total list of sizes (exchange_size).
    def exchangeData(self,neighbour,c):
        self.busy = True
        neighbour.busy = True
        self.ongoing_conn = True
        neighbour.ongoing_conn = True
        self.history[neighbour] = c 
    
        if len(self.exchange_list) > 0:
            message = self.exchange_list[0]
            if message not in neighbour.messages_list:
                neighbour.messages_list.append(message)
                self.exchange_list.remove(message)
                    
        if len(neighbour.exchange_list) > 0:
            message = neighbour.exchange_list[0]
            if message not in self.messages_list:
                self.messages_list.append(message)
                neighbour.exchange_list.remove(message)
            

        # If any of the peers DB has not been totally exchanged we have to store the peer device to keep the connection for next slot
        # print("COMPROBAR---------> ",self.exchange_counter, self.exchange_size, neighbour.exchange_counter, neighbour.exchange_size,len(self.messages_list),len(neighbour.messages_list))
        if len(self.exchange_list) > 0 or len(neighbour.exchange_list) > 0:
            self.prev_peer = neighbour
            self.ongoing_conn = True
            self.prev_peer.ongoing_conn = True
            self.prev_peer.prev_peer = self
            
        # If everything has been exchanged, reset parameters
        if len(self.exchange_list) == 0 and len(neighbour.exchange_list) == 0:
            # print("EVERYTHING HAS BEEN EXCHANGED WITH: ", self.exchange_counter,self.exchange_size)
            # print("ENTRO AQUI", self.exchange_counter, self.exchange_size,neighbour.exchange_counter, neighbour.exchange_size, self.used_memory, self.used_memory)
            if self.connection_duration not in self.scenario.connection_duration_list.keys():
                self.scenario.connection_duration_list[self.connection_duration] = 1
            else:
                self.scenario.connection_duration_list[self.connection_duration] +=1
            # print("CONNEC DURATION normal--> ", self.connection_duration)
            # Add the location of the connection
            if self.current_zoi not in self.scenario.connection_location_list:
                self.scenario.connection_location_list[self.current_zoi] = 1
            else:
                self.scenario.connection_location_list[self.current_zoi] +=1


            self.connection_duration = 0
            neighbour.connection_duration = 0
            self.ongoing_conn = False
            neighbour.ongoing_conn = False
            self.exchange_list = []
            neighbour.exchange_list = []