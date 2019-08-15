import numpy as np
import math 
from collections import Counter 
from collections import OrderedDict
import sys

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
        self.busy = False # busy only per slot
        self.ongoing_conn = False
        self.db_exchange = False
        self.x_list = []
        self.y_list = []
        self.x_list.append(posX)
        self.y_list.append(posY)
        self.speed_list = []
        self.speed_list.append(0)
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
            self.flight_length = np.random.uniform(self.scenario.min_flight_length, self.scenario.max_flight_length)/self.speed
        else:
            self.flight_length = np.inf
        self.vx = 0
        self.vy = 0
        self.x_origin = 0
        self.y_origin = 0
        self.drop = False
        self.time_elapsed = OrderedDict()
        self.connection_duration = 0
        self.max_time_elapsed = max_time_elapsed
        self.myFuture = OrderedDict()
        self.contacts_per_slot = OrderedDict()
        self.calculateZones()
        # self.displayUser()

    
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
            # print("i am ", self.id, "zone: ", z.id)
            d = np.power(self.x_list[-1]- z.x,2) + np.power(self.y_list[-1]- z.y,2)
            if d < z.scenario.square_radius_of_replication:
                self.zones[z] = "replication"
                self.time_elapsed[z.id] = 0
                # print("calculating in replication", self.id)
            if d < z.scenario.square_radius_of_interest:
                self.zones[z] = "interest"
                self.time_elapsed[z.id] = 0
                # print("calculating in interest", self.id)
            if d > z.scenario.square_radius_of_replication:
                if self.ongoing_conn == False: 
                    # if z was stored as a zone, we should remove it because the node is now out 
                    if z in self.zones:
                        del self.zones[z]
                        self.checkDB(z)
                       
                    
    def checkDB(self,z):
        if self.scenario.algorithm == "out": 
            if len(self.messages_list)> 0 and z.id in self.time_elapsed and self.time_elapsed[z.id] == self.max_time_elapsed and self.shouldDrop(z):
                self.messages_list = []
                self.used_memory = 0
                print("Dropping my DB",self.used_memory, self.exchange_size, len(self.messages_list))
            else:
                if z.id in self.time_elapsed:
                    self.time_elapsed[z.id] += 1
                else:
                    self.time_elapsed[z.id] = 1

        if self.scenario.algorithm == "only-in": 
            self.messages_list = []
            self.used_memory = 0
            print("Dropping my DB",self.used_memory, self.exchange_size, len(self.messages_list))


    # Check if the node is in other zoi when time elapsed has passed after leaving the previous zoi
    def shouldDrop(self,z):
        self.drop = True
        for zone in self.zones:
            if z.id != zone.id:
                self.drop = False
        
        # print("drop?", self.drop)
        return self.drop           

    def randomDirection(self):
        # print("My id is: ", self.id)
        # If it is the beggining we need to choose the parameters (direction,etc)
        # print("m--->", self.m)

        if self.isPaused:
            # print("I'm in pause: ", self.pause_counter, self.pause_slots)
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
            
                # print("Id: ", self.id ,"x: ",x, " y: ", y)

                # Use only when we don't want to store every position in the list but only the current position. We are now 
                # storing everything in the previous 2 lines of code.

                # self.x_list[-1]=x
                # self.y_list[-1]=y
                

            if self.m > self.flight_length:
                # print("M----> ", self.m, self.flight_length," PAUSED ")
                self.m = 1
                # self.isPaused = True

    def predict(self,nslots):
        self.list_of_zois_future = []
        for c in range(nslots):
            if c in self.scenario.tracesDic[str(self.id)]:
                items = self.scenario.tracesDic[str(self.id)][c]
                x = items[0]
                y = items[1]
                for z in self.scenario.zois_list:
                    d = np.power(x - z.x,2) + np.power(y - z.y,2)
                    if d < z.scenario.square_radius_of_replication:
                        self.myFuture[c] = z.id
                    if d < z.scenario.square_radius_of_interest:
                        self.myFuture[c] = z.id
                    if d > z.scenario.square_radius_of_replication:
                        if c not in self.myFuture:
                            self.myFuture[c] = -1 
            else:
                self.myFuture[c] = self.myFuture[c-1]
                
        # print('My future: ', self.myFuture.values())  
        self.list_of_zois_future.append(99)
        for v in self.myFuture.values():
            if self.list_of_zois_future[-1] != v:
                self.list_of_zois_future.append(v)     

        # print(self.list_of_zois_future)  


    # Method to read from the traces (stored in the scenario) each node's new position
    # This method will make a node move in every new slot to the next point in the list
    def readTraces(self,c):
        if c in self.scenario.tracesDic[str(self.id)]:
            items = self.scenario.tracesDic[str(self.id)][c]
            x = items[0]
            y = items[1]
            speed = items[2]

            # print("Next point: ", x, y)   
            self.x_list.append(x)
            self.y_list.append(y)
            self.speed_list.append(speed)

        else:
            self.x_list.append(self.x_list[-1])
            self.y_list.append(self.y_list[-1])
            self.speed_list.append(0)

    # method to allow nodes to exchange within a RZ and in the surroundings taking into account a maximum elapse time
    def userContactOut(self,c):
        # print ("First -- My id is ", self.id, " Am I busy for this slot: ", self.busy)

        # Check if the node is not BUSY already for this slot and if the it is in the areas where data exchange is allowed
        if self.busy is False:
            self.neighbours_list = []
            # Find neighbours in this user's tx range
            for user in self.scenario.usr_list:
                if user.id != self.id:
                    pos_user = np.power(user.x_list[-1]-self.x_list[-1],2) + np.power(user.y_list[-1]-self.y_list[-1],2)
                    if pos_user < self.scenario.square_radius_of_tx:
                        # Check if the neighbour is going to the areas where data exchange is required
                        # if drop attribute is False means that he is going to that other area and keeping the content in its DB
                        if user.drop is False:
                            self.neighbours_list.append(user)
                            # print("This is my neighbour: ", user.id, user.busy)

            # Suffle neighbours list to void connecting always to the same users
            np.random.shuffle(self.neighbours_list)

            # Once we have the list of neighbours, first check if there is a previous connection ongoing and the peer is still inside my tx range
            # which is the same as being in the neighbours list since we checked the positions above
            if self.ongoing_conn == True and self.prev_peer in self.neighbours_list:
                # print("I have a prev peer and it is still close. ", self.prev_peer.id)
                self.connection_duration += 1
                self.prev_peer.connection_duration += 1
                # keep exchanging
                self.db_exchange = False
                self.prev_peer.db_exchange = False
                if self.exchange_size == 0 and self.prev_peer.exchange_size == 0:
                    self.hand_shake = self.hand_shake - 1
                    self.prev_peer.hand_shake = self.prev_peer.hand_shake-1
                    # print("NOTHING TO EXCHANGE already loop", self.hand_shake, self.hand_shake_counter)
                # else:
                    # print("THINGS TO EXCHANGE already looop", self.hand_shake, self.hand_shake_counter)
                    
                self.exchangeData(self.prev_peer)

            # else exchange data with a channel rate per slot
            else:
                # if my prev peer is not in my communication range we don't exchange data anymore
                if self.ongoing_conn == True and self.prev_peer not in self.neighbours_list:
                    # print("I have a prev peer and it is far. ", self.prev_peer.id)
                    if self.connection_duration not in self.scenario.connection_duration_list.keys():
                        self.scenario.connection_duration_list[self.connection_duration] = 1
                    else:
                        self.scenario.connection_duration_list[self.connection_duration] +=1

                    # print("CONNEC DURATION FAR PEER--> ", self.connection_duration)
                    #if the duration of connection is the hand shake plus only one slot in this section, it means that there were something
                    # else to exchange and it didn't work
                    if self.connection_duration == self.hand_shake + 1:
                        self.scenario.count_0_exchange_conn += 1 

                    self.connection_duration = 0
                    self.prev_peer.connection_duration = 0
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
                    self.hand_shake_counter = 0
                    self.prev_peer.hand_shake_counter = 0

                # Continue looking for neighbours   
                # print("Neighbour list: ", len(self.neighbours_list))
                # In case we want to connect with more than one neighbour we need to run a loop. Now we only select one neighbour from the list.
                neighbour = None
                for neig in self.neighbours_list:
                        if not neig.busy and neig.ongoing_conn == False:
                            neighbour = neig
                            # print("I found a peer not busy and without ongoing connection. ", neighbour.id)
                            break
                if neighbour != None:
                    self.scenario.attempts +=1
                    # print("Attempts--- ", self.scenario.attempts)
                    self.connection_duration += 1
                    neighbour.connection_duration +=  1
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
                        if m not in neighbour.messages_list: 
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
                    # Count in advance if the connection is going to be useful or not, it means if they have something to exchange.
                    #In case we have nothing to exchange we use the last slot for the checking
                    if self.exchange_size == 0 and neighbour.exchange_size == 0:
                        self.hand_shake = self.hand_shake - 1
                        neighbour.hand_shake = neighbour.hand_shake-1
                        self.scenario.count_non_useful +=1
                        # print("NOTHING TO EXCHANGE", self.hand_shake, self.hand_shake_counter)

                    else:
                        # print("THINGS TO EXCHANGE", self.hand_shake, self.hand_shake_counter)
                        self.scenario.count_useful +=1

                    self.exchangeData(neighbour)

    # method to allow nodes to exchange within a RZ
    def userContact(self,c):
        # print ("My id is ", self.id, " Am I busy for this slot: ", self.busy)
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
                if pos_user < self.scenario.square_radius_of_tx:
                    self.contacts_per_slot[c].append(user.id)

        # Check if the node is not BUSY already for this slot and if the it is in the areas where data exchange is allowed
        if self.busy is False and len(my_rep_zones)>0:
            self.neighbours_list = []
            # Find neighbours in this user's tx range
            for user in self.scenario.usr_list:
                if user.id != self.id:
                    pos_user = np.power(user.x_list[-1]-self.x_list[-1],2) + np.power(user.y_list[-1]-self.y_list[-1],2)
                    if pos_user < self.scenario.square_radius_of_tx:
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
                            # print("This is my neighbour: ", user.id, user.busy)

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
                if self.exchange_size == 0 and self.prev_peer.exchange_size == 0:
                    self.hand_shake = self.hand_shake - 1
                    self.prev_peer.hand_shake = self.prev_peer.hand_shake-1
                    # print("NOTHING TO EXCHANGE already loop", self.hand_shake, self.hand_shake_counter)
                # else:
                    # print("THINGS TO EXCHANGE already looop", self.hand_shake, self.hand_shake_counter)
                    
                self.exchangeData(self.prev_peer)

            # else exchange data with a probability and within a channel rate per slot
            else:
                # if my prev peer is not in my communication range we don't exchange data anymore
                if self.ongoing_conn == True and self.prev_peer not in self.neighbours_list:
                    # print("I have a prev peer and it is far. ", self.prev_peer.id)
                    if self.connection_duration not in self.scenario.connection_duration_list.keys():
                        self.scenario.connection_duration_list[self.connection_duration] = 1
                    else:
                        self.scenario.connection_duration_list[self.connection_duration] +=1

                    # print("CONNEC DURATION FAR PEER--> ", self.connection_duration)
                    #if the duration of connection is the hand shake plus only one slot in this section, it means that there were something
                    # else to exchange and it didn't work
                    if self.connection_duration == self.hand_shake + 1:
                        self.scenario.count_0_exchange_conn += 1 

                    self.connection_duration = 0
                    self.prev_peer.connection_duration = 0
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
                    self.hand_shake_counter = 0
                    self.prev_peer.hand_shake_counter = 0

                # Continue looking for neighbours   
                # print("Neighbour list: ", len(self.neighbours_list))
                # In case we want to connect with more than one neighbour we need to run a loop. Now we only select one neighbour from the list.
                neighbour = None
                for neig in self.neighbours_list:
                        if not neig.busy and neig.ongoing_conn == False:
                            neighbour = neig
                            # print("I found a peer not busy and without ongoing connection. ", neighbour.id)
                            break
                if neighbour != None:
                    self.scenario.attempts +=1
                    # print("Attempts--- ", self.scenario.attempts)
                    self.connection_duration += 1
                    neighbour.connection_duration +=  1
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
                        if m not in neighbour.messages_list: # and m.zoi in neighbour.zones.keys(): # Does not work for connected zois
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
                    # Count in advance if the connection is going to be useful or not, it means if they have something to exchange.
                    #In case we have nothing to exchange we use the last slot for the checking
                    if self.exchange_size == 0 and neighbour.exchange_size == 0:
                        self.hand_shake = self.hand_shake - 1
                        neighbour.hand_shake = neighbour.hand_shake-1
                        self.scenario.count_non_useful +=1
                        # print("NOTHING TO EXCHANGE", self.hand_shake, self.hand_shake_counter)

                    else:
                        # print("THINGS TO EXCHANGE", self.hand_shake, self.hand_shake_counter)
                        self.scenario.count_useful +=1

                    self.exchangeData(neighbour)
                        
                    
    # Method to check which DB is smaller and start exchanging it. 
    # At this point We have the messages to be exchange (exchange_list) and the total list of sizes (exchange_size).

    def exchangeData(self,neighbour):
        self.busy = True
        neighbour.busy = True
        self.ongoing_conn = True
        neighbour.ongoing_conn = True

        if self.hand_shake_counter < self.hand_shake:
            # print("ENTRO EN HANDSHAKE: ", self.id,neighbour.id, self.hand_shake_counter,self.hand_shake,self.connection_duration)
            self.hand_shake_counter += 1
            neighbour.hand_shake_counter += 1
            self.prev_peer = neighbour
            self.ongoing_conn = True
            self.prev_peer.ongoing_conn = True
            self.prev_peer.prev_peer = self
            # print(self.busy, "hand shake not entry: ",self.hand_shake_counter, "neighbour size --> ", neighbour.exchange_size, self.exchange_size, neighbour.exchange_counter, self.exchange_counter)
            
        else:
            # print(self.busy, "hand shake entry: ",self.hand_shake_counter, "neighbour size --> ", neighbour.exchange_size, self.exchange_size, neighbour.exchange_counter, self.exchange_counter)
            if self.exchange_size == 0 and neighbour.exchange_size == 0:
                # print("ENTRO DIRECTAMENTE EN 0 PARA EXCHANGE -- ", self.connection_duration)
                self.db_exchange = True
                neighbour.db_exchange= True

            if self.exchange_size <= neighbour.exchange_size and self.db_exchange is False:
                howMany = 0
                howMany1 = 0
                howMany2 = 0

                # print("My db is smaller than neighbours ", self.exchange_size)
                if self.exchange_size == 0:
                    self.db_exchange = True
                else: 
                    #########################################################################################################
                    if (self.exchange_counter < self.exchange_size):
                        howMany = self.exchange_size - self.exchange_counter
                        howMany1 = self.exchange_size - self.exchange_counter
                        howMany2 = self.exchange_size - self.exchange_counter

                        # Check if the amount of bits to transfer (self.exchange_size) fits in the available channel rate
                        if (howMany > ((self.scenario.mbs/2) - self.scenario.used_mbs)):
                            howMany1 = (self.scenario.mbs/2) - self.scenario.used_mbs
                            # print("1 Mensaje mas grande que mbs, para que quepa: ",howMany1)
                        if (neighbour.used_memory + howMany > neighbour.total_memory):
                            howMany2 = neighbour.total_memory - neighbour.used_memory
                            # print("1 Mensaje mas grande que memoria, para que quepa: ",howMany2)

                        howMany = min(howMany1,howMany2)
                        
                        self.exchange_counter += howMany
                        self.scenario.used_mbs += howMany
                        neighbour.used_memory += howMany

                        self.db_exchange = True 
                        # print("I send X bits: ", self.exchange_counter)
                        # print("used memory: ", neighbour.used_memory) 
                        # print(self.scenario.mbs, self.scenario.used_mbs)

                self.scenario.used_mbs_per_slot.append(self.scenario.used_mbs)   
                #########################################################################################################
                # print("Now we continue with Neigbours db", neighbour.exchange_size)
                if neighbour.exchange_size == 0:
                    neighbour.db_exchange = True
                else:
                    if (neighbour.exchange_counter < neighbour.exchange_size):
                        howMany = neighbour.exchange_size - neighbour.exchange_counter
                        howMany1 = neighbour.exchange_size - neighbour.exchange_counter
                        howMany2 = neighbour.exchange_size - neighbour.exchange_counter

                        # Check if the amount of bits to transfer (neighbour.exchange_size) fits in the available channel rate
                        if(howMany > (self.scenario.mbs - self.scenario.used_mbs)):
                            howMany1 = self.scenario.mbs - self.scenario.used_mbs
                            # print("2 Mensaje mas grande que mbs, para que quepa: ",howMany1)
                        if (self.used_memory + howMany > self.total_memory):
                            howMany2 = self.total_memory - self.used_memory
                            # print("2 Mensaje mas grande que memoria, para que quepa: ",howMany2)
           

                        howMany = min(howMany1,howMany2)
                    
                        neighbour.exchange_counter += howMany
                        neighbour.scenario.used_mbs += howMany
                        self.used_memory += howMany
                        
                        neighbour.db_exchange = True  
                        # print("Neighbour sends me X bits: ", neighbour.exchange_counter)
                        # print("used memory: ", self.used_memory)
                        # print(self.scenario.mbs, self.scenario.used_mbs)
                neighbour.scenario.used_mbs_per_slot.append(howMany)
            #########################################################################################################
            if neighbour.exchange_size < self.exchange_size and neighbour.db_exchange is False:
                howMany = 0
                howMany1 = 0
                howMany2 = 0
                # print("Neighbour db is smaller than mine", neighbour.exchange_size)
                if neighbour.exchange_size == 0:
                    neighbour.db_exchange = True
                else:
                    if (neighbour.exchange_counter < neighbour.exchange_size):
                        howMany = neighbour.exchange_size - neighbour.exchange_counter
                        howMany1 = neighbour.exchange_size - neighbour.exchange_counter
                        howMany2 = neighbour.exchange_size - neighbour.exchange_counter

                        if(howMany > ((self.scenario.mbs/2) - self.scenario.used_mbs)):
                            howMany1 = (self.scenario.mbs/2) - self.scenario.used_mbs
                            # print("3 Mensaje mas grande que mbs, para que quepa: ",howMany1)
                        if(self.used_memory + howMany > self.total_memory):
                            howMany2 = self.total_memory - self.used_memory
                            # print("3 Mensaje mas grande que memory, para que quepa: ",howMany2)
                    
                        
                        howMany = min(howMany1,howMany2)
                         
                        neighbour.exchange_counter += howMany
                        neighbour.scenario.used_mbs += howMany
                        self.used_memory += howMany

                        neighbour.db_exchange = True  
                        # print("Neighbour sends me one bit: ", neighbour.exchange_counter)
                        # print("used memory: ", self.used_memory)
                        # print(self.scenario.mbs, self.scenario.used_mbs)
                neighbour.scenario.used_mbs_per_slot.append(self.scenario.used_mbs)
                #########################################################################################################
                # print("Now we continue with my db", self.exchange_size)
                if self.exchange_size == 0:
                    self.db_exchange = True
                else:
                    if (self.exchange_counter < self.exchange_size):
                        howMany = self.exchange_size - self.exchange_counter
                        howMany1 = self.exchange_size - self.exchange_counter
                        howMany2 = self.exchange_size - self.exchange_counter
                        
                        if(howMany > (self.scenario.mbs - self.scenario.used_mbs)):
                            howMany1 = self.scenario.mbs - self.scenario.used_mbs
                            # print("4 Mensaje mas grande que mbs, para que quepa: ",howMany1)
                        if(neighbour.used_memory + self.exchange_size > neighbour.total_memory):
                            howMany2 = neighbour.total_memory - neighbour.used_memory
                            # print("4 Mensaje mas grande que memory, para que quepa: ",howMany2)
                        
                        howMany = min(howMany1,howMany2)
                       
                        self.exchange_counter += howMany
                        neighbour.used_memory += howMany
                        self.scenario.used_mbs += howMany

                        self.db_exchange = True  
                        # print("I send one bit: ", self.exchange_counter)
                        # print("used memory: ", neighbour.used_memory)
                        # print(self.scenario.mbs, self.scenario.used_mbs)
                self.scenario.used_mbs_per_slot.append(howMany)
                #########################################################################################################

            # Now we exchange the db based on the already exchanged bytes of messages
            # if (len(self.counter_list) != len(self.exchange_list)):
            #     print("LEEEEEEEN--> ", len(self.counter_list),len(neighbour.counter_list), len(self.exchange_list) , len(neighbour.exchange_list) )

            if len(self.exchange_list) > 0:
                for i in range(0,len(self.counter_list)): 
                    # print(i)
                    # print("my counter list de i",self.counter_list[i])
                    # print("my exchange counter", self.exchange_counter) 
                    # print("len of my exchange list",len(self.exchange_list))

                    if (self.counter_list[i] <= self.exchange_counter):
                        if (self.exchange_list[i] not in neighbour.messages_list):
                            # print("Adding message to neighbour DB: ", self.exchange_list[i].size, self.connection_duration,neighbour.connection_duration,len(neighbour.messages_list))
                            neighbour.messages_list.append(self.exchange_list[i])
                    if(self.counter_list[i] == self.exchange_counter):
                        break
                        
            if len(neighbour.exchange_list) > 0:
                for j in range(0,len(neighbour.counter_list)):
                    # print(j)
                    # print("neighbour counter list de j ",neighbour.counter_list[j]) 
                    # print("neighbourg exchange counter ",neighbour.exchange_counter)
                    # print("len of neighbourg exchange list",len(neighbour.exchange_list))

                    if (neighbour.counter_list[j] <= neighbour.exchange_counter): 
                        if (neighbour.exchange_list[j] not in self.messages_list):
                            # print("Adding message to my DB: ", neighbour.exchange_list[j].size, self.connection_duration,neighbour.connection_duration,len(self.messages_list))
                            self.messages_list.append(neighbour.exchange_list[j])
                    if(neighbour.counter_list[j] == neighbour.exchange_counter):
                        break

            # After exchanging both peers part of the db, set back the booleans for next slot
            self.db_exchange = False
            neighbour.db_exchange = False
            # Set back the used mbs for next data exchange for next slot
            self.scenario.used_mbs = 0

            # If any of the peers DB has not been totally exchanged we have to store the peer device to keep the connection for next slot
            # print("COMPROBAR---------> ",self.exchange_counter, self.exchange_size, neighbour.exchange_counter, neighbour.exchange_size,len(self.messages_list),len(neighbour.messages_list))
            if self.exchange_counter < self.exchange_size or neighbour.exchange_counter < neighbour.exchange_size:
                self.prev_peer = neighbour
                # print(" PASSING NEIGHBOUR TO PREV DB", neighbour.id, self.prev_peer.id, neighbour == self.prev_peer)
                self.ongoing_conn = True
                self.prev_peer.ongoing_conn = True
                self.prev_peer.prev_peer = self
                
            # If everything has been exchanged, reset parameters
            if (self.exchange_counter == self.exchange_size and neighbour.exchange_counter == neighbour.exchange_size) or (self.total_memory == self.used_memory and neighbour.total_memory == neighbour.used_memory):
                # print("EVERYTHING HAS BEEN EXCHANGED WITH: ", self.exchange_counter,self.exchange_size)
                # print("ENTRO AQUI", self.exchange_counter, self.exchange_size,neighbour.exchange_counter, neighbour.exchange_size, self.used_memory, self.used_memory)
                if self.connection_duration not in self.scenario.connection_duration_list.keys():
                    self.scenario.connection_duration_list[self.connection_duration] = 1
                else:
                    self.scenario.connection_duration_list[self.connection_duration] +=1
                # print("CONNEC DURATION normal--> ", self.connection_duration)

        
                self.connection_duration = 0
                neighbour.connection_duration = 0
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




    