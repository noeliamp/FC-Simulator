from Zoi import Zoi
import numpy as np
from collections import OrderedDict
import re


class Scenario:
    'Common base class for all scenarios'

    def __init__(self, radius_of_interest, radius_of_replication, radius_of_persistence, max_area, speed_distribution,pause_distribution,min_pause,max_pause,
    min_speed,max_speed,delta,radius_of_tx,channel_rate,num_users,min_flight_length, max_flight_length,flight_length_distribution, hand_shake,num_zois,traces_folder,num_slots):
        # print ("Creating new scenario...")
        self.num_slots = num_slots
        self.square_radius_of_interest = radius_of_interest*radius_of_interest
        self.square_radius_of_replication = radius_of_replication*radius_of_replication
        self.square_radius_of_persistence = radius_of_persistence*radius_of_persistence
        self.radius_of_interest = radius_of_interest
        self.radius_of_replication = radius_of_replication
        self.radius_of_persistence = radius_of_persistence
        self.max_area = max_area
        self.speed_distribution = speed_distribution
        self.pause_distribution = pause_distribution
        self.min_speed = min_speed
        self.max_speed = max_speed
        self.min_pause = min_pause
        self.max_pause = max_pause
        self.delta = delta         # slot time
        self.radius_of_tx = radius_of_tx
        self.square_radius_of_tx = radius_of_tx*radius_of_tx
        self.usr_list = []
        self.channel_rate =  channel_rate
        self.mbs = self.delta*self.channel_rate
        self.used_mbs = 0
        self.num_users= num_users
        self.min_flight_length= min_flight_length
        self.max_flight_length = max_flight_length
        self.flight_length_distribution = flight_length_distribution
        self.hand_shake = hand_shake
        self.used_mbs_per_slot = []
        self.zois_list = []
        self.num_zois = num_zois
        self.tracesDic = OrderedDict()
        self.attempts = 0
        self.count_0_exchange_conn = 0
        self.count_non_useful = 0
        self.count_useful = 0
        self.connection_duration_list = OrderedDict()
        self.list_of_tuples_pos = []

        # If we only define 1 zoi we assume it is going to be located in the center of the scenario
        if self.num_zois == 1:
            zoi = Zoi(0,0,0,self)
            self.zois_list.append(zoi)

        # If we define more than one zoi, we should know if they are going to be based on map points or random uniform distribution
        if self.num_zois > 1:
            # In case we are running simulations based on maps points
            if traces_folder != "none":
                f=open('traces/POIS/POI.wkt',"r")
                lines=f.readlines()
                # First we read the points from the file
                for line in lines:
                    if line.startswith("POINT"):
                        num = re.findall(r'\d+(?:\.\d*)?', line)
                        numbers = [] 
                        numbers.append(float(num[0]))
                        numbers.append(float(num[1]))

                        self.list_of_tuples_pos.append(numbers)
                print('POINTS ', self.list_of_tuples_pos)
                # Second, we create the zois according to the points
                for i in range(0,len(self.list_of_tuples_pos)):
                    zoi = Zoi(i, self.list_of_tuples_pos[i][0],self.list_of_tuples_pos[i][1],self)
                    self.zois_list.append(zoi)

            # In case we are running simulations with zois in random positions within the scenario
            else:
                for i in range(0,self.num_zois):
                    zoi = Zoi(i, np.random.uniform(-self.max_area + self.radius_of_persistence, self.max_area - self.radius_of_persistence),
                    np.random.uniform(-self.max_area + self.radius_of_persistence, self.max_area - self.radius_of_persistence),self)
                    self.zois_list.append(zoi)

        # self.displayScenario()

    def displayScenario(self):
        print("Radius of interest : ", self.radius_of_interest,  ", Radius of replication: ", self.radius_of_replication, 
              ", Radius of persistence: ", self.radius_of_persistence,", Max area: ", self.max_area, ", Min speed: ", self.min_speed, 
              ", Max speed: ", self.max_speed, ", Max pause: ", self.max_pause, ", Min pause: ", self.max_pause, ", Delta: ", self.delta, 
              ", Radious of tx: ", self.radius_of_tx, ", Mbs: ", self.mbs, ", Used Mbs: ", self.used_mbs, 
              ", Channel rate: ", self.channel_rate, ", ZOIS: ", self.num_zois)


    # Traces parser for each scenario, we parse the traces after the scenario creation, depending on which folder (map) and file (specific traces for a given seed in that map)
    def parseTraces(self, folder, file):
        f=open('traces/' + folder + '/'+ file +'_MovementNs2Report.txt',"r")
        lines=f.readlines()
        count = 0
        for line in lines:
            lp = line.split()
            if "at" not in line: 
                node = line[line.find("(")+1:line.find(")")]
                if "X_" in line:
                    x = float(lp[3])
                if "Y_" in line:
                    y = float(lp[3])
                time = float(0)
                speed = float(0)
                count += 1
            else:
                count = 2
                node = line[line.find("(")+1:line.find(")")]
                time = float(lp[2])
                x = float(lp[5])
                y = float(lp[6])
                speed = float(lp[7][:-1])

            # We add the line info to each node dictionary
            if count == 2:
                count = 0
                if node not in self.tracesDic:
                    self.tracesDic[node] = OrderedDict()
                    
                # Stop storing positions if we already have 10000 slots     
                if len(self.tracesDic[node]) <= 10000:
                    self.tracesDic[node][time] = [x,y,speed]
            # print("node ", node , "time", time , "x", x, "y",y, "speed", speed)


           






