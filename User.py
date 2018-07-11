import numpy as np
from Scenario import Scenario
from Message import Message
import math  
from random import shuffle


class User:
    'Common base class for all users'
    

    def __init__(self, id, posX, posY, scenario, max_memory,max_message_size):
        print ("Creating new user...")
        self.id = id
        self.scenario = scenario
        self.total_memory = np.random.uniform(1,max_memory) 
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
            self.speed = np.random.uniform(0,1)
        if self.scenario.pause_distribution == "uniform":
            self.pause_slots = np.random.uniform(self.scenario.min_pause,self.scenario.max_pause)
        self.pause_slots = 0
        self.pause_counter = 1
        self.isPaused = False
        self.N12 = 100            # slots to reach target position (x2,y2) 
        self.n = 1              # current slot within N12 for random waypoint
        self.m = 1              # current slot for random Direction
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
        self.calculateZone()
        self.displayUser()


    def displayUser(self):
        print("ID : ", self.id,  ", Total Memory: ", self.total_memory,  ", Used Memory: ", self.used_memory, ", PosX: ",self.x_list, 
              ", PosY: ", self.y_list, ", Zone: ", self.zone, ", Is Paused: ", self.isPaused, ", Slots Paused: ", self.pause_slots, 
              ", Counter Paused: ", self.pause_counter, ", slot n: ", self.n, ", Message list: " , len(self.messages_list), ", Coordinates list: " , len(self.x_list))

    def calculateZone(self):
        pos = np.power(self.x_list[-1],2) + np.power(self.y_list[-1],2)
          
        if pos < np.power(self.scenario.radius_of_persistence,2):
            self.zone = "persistence"
        if pos < np.power(self.scenario.radius_of_replication,2):
            self.zone= "replication"
        if  pos < np.power(self.scenario.radius_of_interest,2):
            self.zone = "interest"
        if pos > np.power(self.scenario.radius_of_persistence,2):
            self.zone = "outer"
            self.messages_list = []
            self.exchange_list = []
            self.db_exchange = False
            self.exchange_size = 0
            self.used_memory = 0
            # print("Dropping my DB")

    def getNextWayPoint(self):
        if self.scenario.user_generation_distribution == "uniform":
            self.x2 = np.random.uniform(-self.scenario.max_area-2,self.scenario.max_area+2)
            self.y2 = np.random.uniform(-self.scenario.max_area-2,self.scenario.max_area+2)

    def randomWaypoint(self):
        print ("My id is ", self.id)
        # Check if the node is not in his pause period
        if self.isPaused is False:
            # if it is the first time that the user is moving from origin (x1,y1), 
            # we need to  calculate target position (x2,y2) and the number of slots to reach target position (only at the beginning)
            if self.rebound_counter==0 and self.n==1:
                self.randomWaypointParameters()
                print("List of bound x--> ", self.xb)
                print("List of bound y--> ", self.yb)


            # Once we have all the border points and target point (from mobilityParameters method) we start computing the distances
            if self.rebound_counter < len(self.xb)-1:
                print("REBOUND COUNTER: ", self.rebound_counter)
                print("REBOUND LIST LEN: ", len(self.xb), " n-->", self.n )
                
                # If we are at the beggining of a path between 2 points, 
                # save source and destination coordinates and N12 as self information for the following slots (It is going to be the same until n = N12)
                if self.n == 1:
                    print("Entering in n == 1 for a new rebound")
                    self.xs = self.xb[self.rebound_counter]
                    self.ys = self.yb[self.rebound_counter]
                    self.xd = self.xb[self.rebound_counter + 1]
                    self.yd = self.yb[self.rebound_counter + 1]
                    print(self.xs, self.ys, self.xd, self.yd)
                    # Distance between 2 points
                    dist = np.sqrt(np.power((self.xb[self.rebound_counter+1]-self.xb[self.rebound_counter]),2) + 
                                   np.power((self.yb[self.rebound_counter+1]-self.yb[self.rebound_counter]),2))
                    # Time to move from (xb1,yb1) to (xb2,yb2)
                    self.T12 = dist/self.speed
                    # connection establishment time variable
                    # conn_stbl = np.random.uniform() # --> where to include this?
                    # Number of slots to reach (xb2,yb2)
                    self.N12 = np.ceil((self.T12/self.scenario.delta))
                    print("Number of slots until target/border position N12 --> %d" % self.N12)

                if self.N12 == 0:
                    print("N12 = 0, why?")
                # we need to find the new intermediate position between n and n-1 regarding user speed
                # Euclidean vector ev = (x2-x1,y2-y1) and next position after one time slot (xi,yi) = (x1,y1) + n/N12 * ev
                xi = self.xs + (self.n/self.N12) * (self.xd - self.xs)   
                yi = self.ys + (self.n/self.N12) * (self.yd - self.ys)
                print("xi --> " , xi)
                print("yi --> " , yi)
           
                # Once the intermediate position (xi,yi) is selected, add the coordinates to the lists
                self.x_list.append(xi)
                self.y_list.append(yi)

                self.n = self.n + 1

                # if we have reached a bound position, update the counters to start again with the next
                if self.n == self.N12 + 1:
                    self.n = 1
                    self.N12 = 0
                    self.rebound_counter = self.rebound_counter + 1
                    print("rebound_counter: ",self.rebound_counter)
                    print("Bound position reached, n = 0.")
                    

            if self.rebound_counter == len(self.xb)-1:
                self.isPaused = True
                self.rebound_counter = 0
                self.xb = []
                self.yb = []
                print("Final target position reached, rebound counter = 0, Node is paused.")
            

        if self.isPaused:
            self.pause_counter = self.pause_counter + 1
            if self.pause_counter == self.pause_slots:
                self.isPaused = False
                self.pause_counter = 0
    
        # Check the new point zone and print the info of the user
        self.calculateZone()
        # self.displayUser()


    # with this method we create two lists xb and yb at the beggining of the mobility with all the border and targer positions of the user
    def randomWaypointParameters(self):
        self.getNextWayPoint()            
        print("X2: ",self.x2, ", Y2: ", self.y2)
        # Save current position
        self.xb.append(self.x_list[-1]) 
        self.yb.append(self.y_list[-1])
        # If we have a target position out of bounds we need to get first the point in the border
        # in order to follow the rebounding path
        while (self.x2 > self.scenario.max_area) or (self.y2 > self.scenario.max_area) or (self.x2 < -self.scenario.max_area) and (self.y2 < -self.scenario.max_area):
            print("POSITION OUT OF BOUNDS")
            # get the point in the border with the equation of a line (y = mx + n)
            # we need to add all border points in a list in case we have more than one
            if len(self.xb) == 1: 
                print("Entering first check - no rebound yet")
                m = (self.y2 - self.y_list[-1]) / (self.x2 - self.x_list[-1])
                n = self.y_list[-1] - (m*self.x_list[-1])
            else:
                print("Entering rebound")
                m = (self.y2 - self.yb[-1]) / (self.x2 - self.xb[-1])
                n = self.yb[-1] - (m*self.xb[-1])

            if self.x2 > self.scenario.max_area:                    # out from righ side
                if self.y2 > self.scenario.max_area:                # out from the upper right corner
                    self.xb.append(self.scenario.max_area)          # xb and yb coordinates in the corner
                    self.yb.append(self.scenario.max_area)
                    x_out = self.x2 - self.scenario.max_area
                    y_out = self.y2 - self.scenario.max_area
                    self.x2 = self.scenario.max_area - x_out
                    self.y2 = self.scenario.max_area - y_out
                else:
                    self.xb.append(self.scenario.max_area)          # xb and yb coordinates in the border
                    self.yb.append((m*self.xb[-1]) + n)
                    x_out = self.x2 - self.scenario.max_area
                    self.x2 = self.scenario.max_area - x_out

            if self.x2 < -self.scenario.max_area:                   # out from left side
                if self.y2 < -self.scenario.max_area:               # out from the lower left corner
                    self.xb.append(-self.scenario.max_area)         # xb and yb coordinates in the corner
                    self.yb.append(-self.scenario.max_area)         
                    x_out = self.x2 - (-self.scenario.max_area)
                    y_out = self.y2 - (-self.scenario.max_area)
                    self.x2 = -self.scenario.max_area - x_out
                    self.y2 = -self.scenario.max_area - y_out
                else:
                    self.xb.append(-self.scenario.max_area)         # xb and yb coordinates in the border
                    self.yb.append((m*self.xb[-1]) + n)
                    x_out = self.x2 - (-self.scenario.max_area)
                    self.x2 = -self.scenario.max_area - x_out

            if self.y2 < -self.scenario.max_area:                   # out from bottom side
                if self.x2 > self.scenario.max_area:                # out from the lower right corner
                    self.xb.append(self.scenario.max_area)          # xb and yb coordinates in the corner
                    self.yb.append(-self.scenario.max_area)
                    x_out = self.x2 - self.scenario.max_area
                    y_out = self.y2 - (-self.scenario.max_area)
                    self.x2 = self.scenario.max_area - x_out
                    self.y2 = -self.scenario.max_area - y_out
                else:
                    self.yb.append(-self.scenario.max_area)         # xb and yb coordinates in the border
                    self.xb.append((self.yb[-1]-n)/m)
                    y_out = self.y2 - (-self.scenario.max_area)
                    self.y2 = -self.scenario.max_area - y_out
            
            if self.y2 > self.scenario.max_area:                    # out from top side
                if self.x2 < -self.scenario.max_area:               # out from the upper left corner
                    self.xb.append(-self.scenario.max_area)         # xb and yb coordinates in the corner
                    self.yb.append(self.scenario.max_area)
                    x_out = self.x2 - (-self.scenario.max_area)
                    y_out = self.y2 - self.scenario.max_area
                    self.x2 = -self.scenario.max_area - x_out
                    self.y2 = self.scenario.max_area - y_out
                else:
                    self.yb.append(self.scenario.max_area)         # xb and yb coordinates in the border
                    self.xb.append((self.yb[-1]-n)/m)
                    y_out = self.y2 - self.scenario.max_area
                    self.y2 = self.scenario.max_area - y_out


        # Append target possition to the end of the list 
        # (if the target position is never out of bounds this list will only containg the first position and the targer position)
        print("Final target position ----> X2: ", self.x2, ", Y2: ", self.y2)
            
        self.xb.append(self.x2)
        self.yb.append(self.y2)


    def randomDirection(self):
        # print("My id is: ", self.id)
        # If it is the beggining we need to choose the parameters (direction,etc)
        # print("m--->", self.m)

        if self.isPaused:
            # print("I'm in pause: ", self.pause_counter, self.pause_slots)
            self.pause_counter = self.pause_counter + 1 
            if self.pause_counter == self.pause_slots + 1:
                self.isPaused = False
                self.pause_counter = 1

        else:       
            if self.m == 1:
                # generate a flight lenght
                # self.flight_length = np.random.randint(1,10)
                # print("Flight lenght: ", self.flight_length)
                # select an angle
                randNum = np.random.uniform()
                alpha = 360 * randNum *(math.pi/180)
                alpha_deg = 360 * randNum

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
                self.m = self.m + 1

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
        self.calculateZone()

    def userContact(self):
        # print ("My id is ", self.id, " And my zone is: ", self.zone, " Am I busy for this slot: ", self.busy)

        # Check if the node is not BUSY already for this slot and if the user is in the areas where data exchange is allowed
        if self.busy is False and (self.zone == "interest" or self.zone == "replication"):
            self.neighbours_list = []
            # Find neighbours in this user's tx range that are not already busy in this slot
            for user in self.scenario.usrList:
                if user.id != self.id:
                    pos_user = np.power(user.x_list[-1]-self.x_list[-1],2) + np.power(user.y_list[-1]-self.y_list[-1],2)
                    if pos_user < np.power(self.scenario.radius_of_tx,2):
                        # Check if the neighbour is in the areas where data exchange is allowed
                        if user.zone == "interest" or user.zone == "replication":
                            self.neighbours_list.append(user)
                            # print("This is my neighbour: ", user.id, user.zone, user.busy)

            # Suffle neighbours list to void connecting always to the same users
            shuffle(self.neighbours_list)
            # Once we have the list of neighbours, first check if there is a previous connection ongoing and the peer is still around
            if self.ongoing_conn == True and self.prev_peer in self.neighbours_list and self.prev_peer.zone != "outer" and self.prev_peer.zone != "persistence":
                # print("I have a prev peer and it is still close. ", self.prev_peer.id)
                # keep exchanging
                self.db_exchange = False
                self.prev_peer.db_exchange = False
                self.exchangeData(self.prev_peer)

            # else exchange data with a probability and within a channel rate per slot time
            else:
                # if my prev peer is not in my communication range or it is in zones outer/persistence we don't exchange data anymore
                if self.ongoing_conn == True and (self.prev_peer not in self.neighbours_list or self.prev_peer.zone == "outer" or self.prev_peer.zone == "persistence"):
                    # print("I have a prev peer and it is far. ", self.prev_peer.id, self.prev_peer.zone)
                    # If in previous slot we have exchanged bits from next messages we have to remove them from the used memory because we did't manage to
                    # exchange the whole message so we loose it.
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
                    # probability to exchange data with this neighbour
                    self.prob = np.random.uniform()
                    # hand shake needs to be changed to randint variable
                    # self.hand_shake = 80
                    # neighbour.hand_shake = 80

                    # print("Probability to exchange: ", self.prob, " to neighbour: ", neighbour.id)
                    if self.prob > 0.5:
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
                            if m not in neighbour.messages_list:
                                self.exchange_list.append(m)
                                self.exchange_size = self.exchange_size + m.size
                                if len(self.counter_list) == 0:
                                    self.counter_list.append(m.size)
                                else:
                                    self.counter_list.append(self.counter_list[-1]+m.size)
                                    
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


                        # Second, exchange the data with peer!!
                        # print("My exchange db size --> ", self.exchange_size, "Counter list", len(self.counter_list))
                        # print("Neighbour exchange db size --> ", neighbour.exchange_size, "Counter list", len(neighbour.counter_list))
                        self.exchangeData(neighbour)
                    
    # method to check which DB is smaller and start exchanging it. 
    # At this point We have the messages to be exchange (exchange_list) and the total list sizes (exchange_size).
    def exchangeData(self,neighbour):
        self.busy = True
        neighbour.busy = True
        self.ongoing_conn = True
        neighbour.ongoing_conn = True

        if self.hand_shake_counter < self.hand_shake:
            self.hand_shake_counter = self.hand_shake_counter + 1
            neighbour.hand_shake_counter = neighbour.hand_shake_counter + 1
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
                        self.exchange_counter = self.exchange_counter + 1
                        neighbour.used_memory = neighbour.used_memory + 1
                        self.scenario.used_mbs = self.scenario.used_mbs + 1
                        self.db_exchange = True 
                        # print("I send one bit: ", self.exchange_counter)
                        # print("used memory: ", neighbour.used_memory) 
                        # print(self.scenario.mbs, self.scenario.used_mbs)
                    
                # print("Now we continue with Neigbours db", neighbour.exchange_size)
                if neighbour.exchange_size == 0:
                    neighbour.db_exchange = True
                else:
                    while (neighbour.exchange_counter < neighbour.exchange_size) and (self.used_memory + 1 < self.total_memory) and (1 <= (self.scenario.mbs - self.scenario.used_mbs)):
                        neighbour.exchange_counter = neighbour.exchange_counter + 1
                        self.used_memory = self.used_memory + 1
                        neighbour.scenario.used_mbs = neighbour.scenario.used_mbs + 1
                        neighbour.db_exchange = True  
                        # print("Neighbour sends me one bit: ", neighbour.exchange_counter)
                        # print("used memory: ", self.used_memory)
                        # print(self.scenario.mbs, self.scenario.used_mbs)

            if neighbour.exchange_size < self.exchange_size and neighbour.db_exchange is False:
                # print("Neighbour db is smaller than mine", neighbour.exchange_size)
                if neighbour.exchange_size == 0:
                    neighbour.db_exchange = True
                else:
                    while (neighbour.exchange_counter < neighbour.exchange_size) and (self.used_memory + 1 < self.total_memory) and (1 <= ((self.scenario.mbs/2) - self.scenario.used_mbs)):
                        neighbour.exchange_counter = neighbour.exchange_counter + 1
                        self.used_memory = self.used_memory + 1
                        neighbour.scenario.used_mbs = neighbour.scenario.used_mbs + 1
                        neighbour.db_exchange = True  
                        # print("Neighbour sends me one bit: ", neighbour.exchange_counter)
                        # print("used memory: ", self.used_memory)
                        # print(self.scenario.mbs, self.scenario.used_mbs)

                # print("Now we continue with my db", self.exchange_size)
                if self.exchange_size == 0:
                    self.db_exchange = True
                else:
                    while (self.exchange_counter < self.exchange_size) and (neighbour.used_memory + 1 < neighbour.total_memory) and (1 <= (self.scenario.mbs - self.scenario.used_mbs)):
                        self.exchange_counter = self.exchange_counter + 1
                        neighbour.used_memory = neighbour.used_memory + 1
                        self.scenario.used_mbs = self.scenario.used_mbs + 1
                        self.db_exchange = True  
                        # print("I send one bit: ", self.exchange_counter)
                        # print("used memory: ", neighbour.used_memory)
                        # print(self.scenario.mbs, self.scenario.used_mbs)
            
            # Now we exchange the db based on the already exchanged bytes of messages
            # print("LEEEEEEEN--> ", len(self.counter_list),len(neighbour.counter_list), len(self.exchange_list) , len(neighbour.exchange_list) )
            if len(self.exchange_list) > 0:
                for i in range(0,len(self.counter_list)):
                    # print(i)
                    # print(self.counter_list[i], self.exchange_counter, self.exchange_list[i] not in neighbour.messages_list, len(self.exchange_list)>0)
                    if (self.counter_list[i] <= self.exchange_counter) and (self.exchange_list[i] not in neighbour.messages_list) and (len(self.exchange_list)>0):
                        # print("Adding message to neighbour DB: ", self.exchange_list[i].size)
                        neighbour.messages_list.append(self.exchange_list[i])
            if len(neighbour.exchange_list) > 0:
                for j in range(0,len(neighbour.counter_list)):
                    # print(j)
                    # print(neighbour.counter_list[j], neighbour.exchange_counter, neighbour.exchange_list[j] not in self.messages_list,len(neighbour.exchange_list)>0)
                    if (neighbour.counter_list[j] <= neighbour.exchange_counter) and (neighbour.exchange_list[j] not in self.messages_list) and (len(neighbour.exchange_list)>0):
                        # print("Adding message to my DB: ", neighbour.exchange_list[j].size)
                        self.messages_list.append(neighbour.exchange_list[j])

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




 