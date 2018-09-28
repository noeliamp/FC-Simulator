import numpy as np
import math 
from collections import Counter 
from collections import OrderedDict
import sys

class User:
    'Common base class for all users'

    def __init__(self, id, posX, posY, scenario, max_memory):

        print ("Creating new user...")
        self.id = id
        self.scenario = scenario
        self.total_memory = max_memory
        self.messages_list = []
        self.exchange_list = []
        self.exchange_size = 0
        self.prev_peer = None
        self.busy = False # busy only per slot
        self.ongoing_conn = False
        self.db_exchange = False
        self.x_list = []
        self.y_list = []
        self.x_list.append(posX)
        self.y_list.append(posY)
        self.x2 = 0
        self.y2 = 0
        self.xb = []
        self.yb = []
        self.xs = 0
        self.xd = 0
        self.ys = 0
        self.yd = 0
        if self.scenario.speed_distribution == "uniform":
            self.speed = (np.random.uniform(self.scenario.max_speed,self.scenario.min_speed))*self.scenario.delta
        if self.scenario.pause_distribution == "uniform":
            self.pause_slots = np.random.uniform(self.scenario.min_pause,self.scenario.max_pause)
        else:
            self.pause_slots = 0
        self.pause_counter = 1
        self.isPaused = False
        self.N12 = np.inf            # slots to reach target position (x2,y2) 
        self.n = 1                   # current slot within N12 for random waypoint
        self.m = 1                   # current slot for random Direction
        self.rebound_counter = 0
        self.neighbours_list = []
        self.counter_list = []
        self.exchange_counter = 0
        self.used_memory = 0
        self.hand_shake = self.scenario.hand_shake/self.scenario.delta
        self.hand_shake_counter = 0
        self.prob = 0
        if self.scenario.flight_length_distribution == "uniform":
            self.flight_length = np.random.uniform(self.scenario.min_flight_length, self.scenario.max_flight_length)
        else:
            self.flight_length = np.inf
        self.vx = 0
        self.vy = 0
        self.x_origin = 0
        self.y_origin = 0
        self.failures_counter = 0
        self.attempts_counter = 0
        self.connection_duration = 0
        self.connection_duration_list = []
        self.successes_list_A = []
        self.suc = 0
        self.successes_list_B = []
        self.ex_list_print_A = []
        self.ex_list_print_B = []
        self.contacts_per_slot = OrderedDict()
        self.calculateZones()
        self.displayUser()

    
    def displayUser(self):
        print("ID : ", self.id,  ", Total Memory: ", self.total_memory,  ", Used Memory: ", self.used_memory, ", PosX: ",self.x_list, 
              ", PosY: ", self.y_list, ", Is Paused: ", self.isPaused, ", Slots Paused: ", self.pause_slots, 
              ", Counter Paused: ", self.pause_counter, ", slot n: ", self.n, ", Message list: " , len(self.messages_list), ", Coordinates list: " , len(self.x_list))
        for z in self.zones:
            print("ZOI ID: ", z.id)
            print("Zone: ", self.zones[z])
    
    def calculateZones(self):
        self.canIexchange = False
        self.zones = OrderedDict()
        for z in self.scenario.zois_list:
            d = np.power(self.x_list[-1]- z.x,2) + np.power(self.y_list[-1]- z.y,2)
            if d < np.power(z.scenario.radius_of_persistence,2):
                self.zones[z] = "persistence"
            if d < np.power(z.scenario.radius_of_replication,2):
                self.zones[z] = "replication"
            if d < np.power(z.scenario.radius_of_interest,2):
                self.zones[z] = "interest"
            if d > np.power(z.scenario.radius_of_persistence,2):
                # We do not keep information about the zones where the node is out
                # if self.ongoing_conn == False:
                self.deleteMessages(z)

    def deleteMessages(self,z):
        # We remove the messages belonging to this zone in case the node was previously in the zone (the zone existed before)    
        size = 0
        for m in self.messages_list:
            if m.zoi == z:
                size += m.size
                self.messages_list.remove(m)
                if m in self.exchange_list:
                    self.exchange_list.remove(m)
        self.used_memory -= size
        self.exchange_size -= size
        # self.db_exchange = False what to do with this?
        # print("Dropping my DB")


    def randomDirection(self):
        # print("My id is: ", self.id)
        # If it is the beggining we need to choose the parameters (direction,etc)
        # print("m--->", self.m)

        if self.isPaused:
            print("I'm in pause: ", self.pause_counter, self.pause_slots)
            self.pause_counter += 1 
            if self.pause_counter == self.pause_slots + 1:
                self.isPaused = False
                self.pause_counter = 1

        else:       
            if self.m == 1:
                # generate a flight lenght
                # print("My ID: ", self.id)
                # self.flight_length = np.random.randint(self.scenario.min_flight_length,self.scenario.max_flight_length)
                # print("Flight lenght: ", self.flight_length)
                # select an angle
                randNum = np.random.uniform()
                alpha = 360 * randNum *(math.pi/180)
                # alpha_deg = 360 * randNum

                self.x_origin = self.x_list[-1]
                self.y_origin = self.y_list[-1]
                # print("My position: ", self.x_list[-1], self.y_list[-1])
                # print("Angle: ", alpha_deg)

                self.vx = math.cos(alpha)
                self.vy = math.sin(alpha)

                # print("Vector: ", self.vx, self.vy)


            if self.m <= self.flight_length:
                x = (self.vx*self.speed*self.m) + self.x_origin
                y = (self.vy*self.speed*self.m) + self.y_origin
                # print("Next point: ", x, y) 
                m = (y - self.y_origin) / (x - self.x_origin)
                n = y - (m*x)  
                self.m += 1

                if x > self.scenario.max_area:
                    # print("ME SALGO")
                    x = self.scenario.max_area
                    y = m*x + n
                    # self.isPaused = True
                    self.m = 1
                if x < -self.scenario.max_area:
                    # print("ME SALGO")
                    x = - self.scenario.max_area
                    y = m*x + n
                    # self.isPaused = True
                    self.m = 1
                if y > self.scenario.max_area:
                    # print("ME SALGO")
                    y = self.scenario.max_area
                    x = (y-n)/m
                    # self.isPaused = True
                    self.m = 1
                if y < -self.scenario.max_area:
                    # print("ME SALGO")
                    y = - self.scenario.max_area
                    x = (y-n)/m
                    # self.isPaused = True
                    self.m = 1

                # print("Next point: ", x, y)   
                self.x_list.append(x)
                self.y_list.append(y)
                

            if self.m > self.flight_length:
                # print("M----> ", self.m, self.flight_length," PAUSED ")
                self.m = 1
                # self.isPaused = True


        # Check the new point zone of the user
        self.calculateZones()

    def userContact(self,c):
        # print ("My id is ", self.id, " And my zone is: ", self.zone, " Am I busy for this slot: ", self.busy)
        my_rep_zones = []
        my_inter_zones = []
        if "replication" in self.zones.values():
            my_rep_zones.append(list(self.zones.keys())[list(self.zones.values()).index("replication")])
        if "interest" in self.zones.values():
            my_inter_zones.append(list(self.zones.keys())[list(self.zones.values()).index("interest")])

        my_rep_zones.extend(my_inter_zones)

        # Include the neighbours found in this slot for contacts statistics
        for user in self.scenario.usr_list:
            if user.id != self.id:
                pos_user = np.power(user.x_list[-1]-self.x_list[-1],2) + np.power(user.y_list[-1]-self.y_list[-1],2)
                if pos_user < np.power(self.scenario.radius_of_tx,2):
                    self.contacts_per_slot[c].append(user.id)

        # Check if the node is not BUSY already for this slot and if the it is in the areas where data exchange is allowed
        if self.busy is False and len(my_rep_zones)>0:
            self.neighbours_list = []
            # Find neighbours in this user's tx range
            for user in self.scenario.usr_list:
                if user.id != self.id:
                    pos_user = np.power(user.x_list[-1]-self.x_list[-1],2) + np.power(user.y_list[-1]-self.y_list[-1],2)
                    if pos_user < np.power(self.scenario.radius_of_tx,2):
                        # Check if the neighbour is in the areas where data exchange is allowed
                        user_rep_zones = []
                        user_inter_zones = []
                        if "replication" in user.zones.values():
                            user_rep_zones.append(list(user.zones.keys())[list(user.zones.values()).index("replication")])
                        if "interest" in user.zones.values():
                            user_inter_zones.append(list(user.zones.keys())[list(user.zones.values()).index("interest")])

                        user_rep_zones.extend(user_inter_zones)
                        p = set(my_rep_zones)&set(user_rep_zones)
                        if len(p) > 0:
                            self.neighbours_list.append(user)
                            # print("This is my neighbour: ", user.id, user.zone, user.busy)

            # Suffle neighbours list to void connecting always to the same users
            np.random.shuffle(self.neighbours_list)
           
            # Once we have the list of neighbours, first check if there is a previous connection ongoing and the peer is still inside my tx range
            # which is the same as been in the neighbours list since we checked the positions above
            if self.ongoing_conn == True and self.prev_peer in self.neighbours_list:
                # print("I have a prev peer and it is still close. ", self.prev_peer.id)
                self.connection_duration += 1
                self.prev_peer.connection_duration += 1
                # keep exchanging
                self.db_exchange = False
                self.prev_peer.db_exchange = False
                self.exchangeData(self.prev_peer)

            # else exchange data with a probability and within a channel rate per slot
            else:
                # if my prev peer is not in my communication range we don't exchange data anymore
                if self.ongoing_conn == True and self.prev_peer not in self.neighbours_list:
                    # print("I have a prev peer and it is far. ", self.prev_peer.id, self.prev_peer.zone)
                    self.connection_duration_list.append(self.connection_duration)
                    self.successes_list_A.append(self.suc)
                    self.successes_list_B.append(self.prev_peer.suc)

                    self.ex_list_print_A.append(len(self.exchange_list))
                    self.ex_list_print_B.append(len(self.prev_peer.exchange_list))

                    # self.prev_peer.connection_duration_list.append(self.prev_peer.connection_duration)
                    self.connection_duration = 0
                    self.prev_peer.connection_duration = 0
                    self.suc = 0
                    self.prev_peer.suc = 0
                    # If in previous slot we have exchanged bits from next messages we have to remove them from the used memory because we did't manage to
                    # exchange the whole message so we loose it. Basically --> only reset used_memory because the msg has not been added to the list.
                    reset_used_memory = 0
                    for m in self.messages_list:
                        reset_used_memory = reset_used_memory + m.size
                    self.used_memory = reset_used_memory
                    reset_used_memory = 0
                    for m in self.prev_peer.messages_list:
                        reset_used_memory = reset_used_memory + m.size
                    self.prev_peer.used_memory = reset_used_memory

                    # reset all parameters to start clean with a new peer
                    self.exchange_list = []
                    self.prev_peer.exchange_list = []
                    self.exchange_size = 0  
                    self.prev_peer.exchange_size = 0
                    self.db_exchange = False
                    self.prev_peer.db_exchange = False
                    self.ongoing_conn = False
                    self.prev_peer.ongoing_conn = False
                    # Set back the used mbs for next data exchange for next slot
                    self.scenario.used_mbs = 0

                # Continue looking for neighbours   
                # print("Neighbour list: ", len(self.neighbours_list))
                # In case we want to connect with more than one neighbour we need to run a loop. Now we only select one neighbour from the list.
                neighbour = None
                for neig in self.neighbours_list:
                        if not neig.busy and neig.ongoing_conn == False:
                            neighbour = neig
                            # print("I found a peer not busy and without ongoing connection.")
                            break
                if neighbour != None:
                    self.attempts_counter += 1

                    # probability to exchange data with this neighbour
                    self.prob = np.random.uniform()
                    # hand shake needs to be changed to randint variable
                    # self.hand_shake = 80
                    # neighbour.hand_shake = 80

                    # print("Probability to exchange: ", self.prob, " to neighbour: ", neighbour.id)
                    if self.prob > 0.5:
                        self.connection_duration += 1
                        neighbour.connection_duration +=  1
                        # print("my number of messages: ", len(self.messages_list), " LENGTH --> ", self.used_memory)
                        # print("number of messages from neighbour: ", len(neighbour.messages_list), " LENGTH --> ", neighbour.used_memory)
                        self.exchange_size = 0
                        neighbour.exchange_size = 0
                        self.exchange_list = []
                        neighbour.exchange_list = []
                        self.exchange_counter = 0
                        neighbour.exchange_counter = 0
                        self.counter_list = []
                        neighbour.counter_list = []
                        self.db_exchange = False
                        neighbour.db_exchange = False
                        self.scenario.used_mbs = 0
                        # First, check the messages missing in the peers devices and add them to the exchange list of messages of every peer
                        for m in self.messages_list:
                            # print("Neighbour does not have message? ", m not in neighbour.messages_list, m.size, len(self.messages_list))
                            if m not in neighbour.messages_list and m.zoi in neighbour.zones.keys():
                                self.exchange_list.append(m)
                                self.exchange_size = self.exchange_size + m.size
                                if len(self.counter_list) == 0:
                                    self.counter_list.append(m.size)
                                else:
                                    self.counter_list.append(self.counter_list[-1]+m.size)

                        # After choosing the messages that are missing in the peer, we need to shuffle the list
                        np.random.shuffle(self.exchange_list)
                        # print("my number of messages: ", len(self.messages_list), " LENGTH --> ", self.used_memory)
                        # print("number of messages from neighbour: ", len(neighbour.messages_list), " LENGTH --> ", neighbour.used_memory)
                        for m in neighbour.messages_list:
                            # print("I don't have message? ", m not in self.messages_list, m.size,len(neighbour.messages_list))
                            if m not in self.messages_list:
                                neighbour.exchange_list.append(m)
                                neighbour.exchange_size = neighbour.exchange_size + m.size
                                if len(neighbour.counter_list) == 0:
                                    neighbour.counter_list.append(m.size)
                                else:
                                    neighbour.counter_list.append(neighbour.counter_list[-1]+m.size)

                        # After choosing the messages that are missing in the peer, we need to shuffle the list
                        np.random.shuffle(neighbour.exchange_list)

                        # Second, exchange the data with peer!!
                        # print("My exchange db size --> ", self.exchange_size, "Counter list", len(self.counter_list))
                        # print("Neighbour exchange db size --> ", neighbour.exchange_size, "Counter list", len(neighbour.counter_list))
                        self.exchangeData(neighbour)
                    if self.prob <= 0.5:
                        self.failures_counter =  self.failures_counter + 1

        
                    
    # Method to check which DB is smaller and start exchanging it. 
    # At this point We have the messages to be exchange (exchange_list) and the total list sizes (exchange_size).

    def exchangeData(self,neighbour):
        self.busy = True
        neighbour.busy = True
        self.ongoing_conn = True
        neighbour.ongoing_conn = True

        if self.hand_shake_counter < self.hand_shake:
            self.hand_shake_counter += 1
            neighbour.hand_shake_counter += 1
            # print(self.busy, "hand shake not entry: ",self.hand_shake_counter, "neighbour size --> ", neighbour.exchange_size, neighbour.zone, self.exchange_size, neighbour.exchange_counter, self.exchange_counter)
        else:
            # print(self.busy, "hand shake entry: ",self.hand_shake_counter, "neighbour size --> ", neighbour.exchange_size, neighbour.zone, self.exchange_size, neighbour.exchange_counter, self.exchange_counter)
            if self.exchange_size == 0 and neighbour.exchange_size == 0:
                self.db_exchange = True
                neighbour.db_exchange= True

            if self.exchange_size <= neighbour.exchange_size and self.db_exchange is False:
                # print("My db is smaller than neighbours ", self.exchange_size)
                if self.exchange_size == 0:
                    self.db_exchange = True
                else:
                    while (self.exchange_counter < self.exchange_size) and (neighbour.used_memory + 1 <= neighbour.total_memory) and (1 <= ((self.scenario.mbs/2) - self.scenario.used_mbs)):    
                        self.exchange_counter += 1
                        neighbour.used_memory+= 1
                        self.scenario.used_mbs += 1
                        self.db_exchange = True 
                        # print("I send one bit: ", self.exchange_counter)
                        # print("used memory: ", neighbour.used_memory) 
                        # print(self.scenario.mbs, self.scenario.used_mbs)

                self.scenario.used_mbs_per_slot.append(self.scenario.used_mbs)   
                # print("Now we continue with Neigbours db", neighbour.exchange_size)
                cou = 0
                if neighbour.exchange_size == 0:
                    neighbour.db_exchange = True
                else:
                    while (neighbour.exchange_counter < neighbour.exchange_size) and (self.used_memory + 1 < self.total_memory) and (1 <= (self.scenario.mbs - self.scenario.used_mbs)):
                        neighbour.exchange_counter += 1
                        self.used_memory += 1
                        neighbour.scenario.used_mbs += 1
                        neighbour.db_exchange = True  
                        cou += 1
                        # print("Neighbour sends me one bit: ", neighbour.exchange_counter)
                        # print("used memory: ", self.used_memory)
                        # print(self.scenario.mbs, self.scenario.used_mbs)
                neighbour.scenario.used_mbs_per_slot.append(cou)
            if neighbour.exchange_size < self.exchange_size and neighbour.db_exchange is False:
                # print("Neighbour db is smaller than mine", neighbour.exchange_size)
                if neighbour.exchange_size == 0:
                    neighbour.db_exchange = True
                else:
                    while (neighbour.exchange_counter < neighbour.exchange_size) and (self.used_memory + 1 < self.total_memory) and (1 <= ((self.scenario.mbs/2) - self.scenario.used_mbs)):
                        neighbour.exchange_counter += 1
                        self.used_memory += 1
                        neighbour.scenario.used_mbs += 1
                        neighbour.db_exchange = True  
                        # print("Neighbour sends me one bit: ", neighbour.exchange_counter)
                        # print("used memory: ", self.used_memory)
                        # print(self.scenario.mbs, self.scenario.used_mbs)
                neighbour.scenario.used_mbs_per_slot.append(self.scenario.used_mbs)
                # print("Now we continue with my db", self.exchange_size)
                cou= 0
                if self.exchange_size == 0:
                    self.db_exchange = True
                else:
                    while (self.exchange_counter < self.exchange_size) and (neighbour.used_memory + 1 < neighbour.total_memory) and (1 <= (self.scenario.mbs - self.scenario.used_mbs)):
                        self.exchange_counter += 1
                        neighbour.used_memory += 1
                        self.scenario.used_mbs += 1
                        self.db_exchange = True  
                        cou += 1
                        # print("I send one bit: ", self.exchange_counter)
                        # print("used memory: ", neighbour.used_memory)
                        # print(self.scenario.mbs, self.scenario.used_mbs)
                self.scenario.used_mbs_per_slot.append(cou)

            # Now we exchange the db based on the already exchanged bytes of messages
            # print("LEEEEEEEN--> ", len(self.counter_list),len(neighbour.counter_list), len(self.exchange_list) , len(neighbour.exchange_list) )
            if len(self.exchange_list) > 0:
                for i in range(0,len(self.counter_list)):
                    # print(i)
                    # print(self.counter_list[i], self.exchange_counter, self.exchange_list[i] not in neighbour.messages_list, len(self.exchange_list)>0)
                    if self.counter_list[i] <= self.exchange_counter and self.exchange_list[i] not in neighbour.messages_list:
                            # print("Adding message to neighbour DB: ", self.exchange_list[i].size)
                            neighbour.messages_list.append(self.exchange_list[i])
                            self.suc += 1
                        
            if len(neighbour.exchange_list) > 0:
                for j in range(0,len(neighbour.counter_list)):
                    # print(j)
                    # print(neighbour.counter_list[j], neighbour.exchange_counter, neighbour.exchange_list[j] not in self.messages_list,len(neighbour.exchange_list)>0)
                    if neighbour.counter_list[j] <= neighbour.exchange_counter and (neighbour.exchange_list[j] not in self.messages_list):
                            # print("Adding message to my DB: ", neighbour.exchange_list[j].size)
                            self.messages_list.append(neighbour.exchange_list[j])
                            neighbour.suc += 1

        # After exchanging both peers part of the db, set back the booleans for next slot
        self.db_exchange = False
        neighbour.db_exchange = False
        # Set back the used mbs for next data exchange for next slot
        self.scenario.used_mbs = 0

        # If any of the peers DB has not been totally exchanged we have to store the peer device to keep the connection for next slot
        if self.exchange_counter < self.exchange_size or neighbour.exchange_counter < neighbour.exchange_size:
            self.prev_peer = neighbour
            # print(" PASSING NEIGHBOUR TO PREV DB", neighbour.id, self.prev_peer.id, neighbour == self.prev_peer)
            self.ongoing_conn = True
            self.prev_peer.ongoing_conn = True
            self.prev_peer.prev_peer = self
            

        # If everything has been exchanged, reset parameters
        if self.exchange_counter == self.exchange_size and neighbour.exchange_counter == neighbour.exchange_size:
            # print("ENTRO AQUI", self.exchange_counter, self.exchange_size,neighbour.exchange_counter, neighbour.exchange_size, self.used_memory, self.used_memory)
            self.connection_duration_list.append(self.connection_duration)
            self.successes_list_A.append(self.suc)
            self.successes_list_B.append(neighbour.suc)

            self.ex_list_print_A.append(len(self.exchange_list))
            self.ex_list_print_B.append(len(neighbour.exchange_list))

            # neighbour.connection_duration_list.append(neighbour.connection_duration)
            self.connection_duration = 0
            neighbour.connection_duration = 0
            self.suc = 0
            neighbour.suc = 0
            self.ongoing_conn = False
            neighbour.ongoing_conn = False
            self.exchange_list = []
            neighbour.exchange_list = []
            self.db_exchange = False
            neighbour.db_exchange = False
            self.counter_list = []
            neighbour.counter_list = []
            self.exchange_counter = 0
            neighbour.exchange_counter = 0
            self.exchange_size = 0
            neighbour.exchange_size = 0
            self.scenario.used_mbs = 0
            self.hand_shake_counter = 0
            neighbour.hand_shake_counter = 0
            # If they don't have anything to exchange from the beginning they will not be set as busy for this slot.
            # They will remain busy just in case that during this slot they finished exchanging their DB.
            if neighbour.exchange_size == 0 and self.exchange_size == 0:
                self.busy = False
                neighbour.busy = False




 