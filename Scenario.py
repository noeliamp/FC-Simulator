from Zoi import Zoi
import numpy as np
from collections import OrderedDict
import re
import os
from datetime import datetime, timedelta
from User import User
import json


class Scenario:
    'Common base class for all scenarios'

    def __init__(self, radius_of_replication, max_area,delta,radius_of_tx,channel_rate,num_users,num_zois,
                    traces_folder,num_slots, algorithm,max_memory,max_time_elpased,gamma,statis):
        # print ("Creating new scenario...")
        self.num_slots = num_slots
        self.square_radius_of_replication = radius_of_replication*radius_of_replication
        self.radius_of_replication = radius_of_replication
        self.max_area = max_area
        self.delta = delta        
        self.radius_of_tx = radius_of_tx
        self.square_radius_of_tx = radius_of_tx*radius_of_tx
        self.usr_list = []
        self.helper_usr_list = []
        self.channel_rate =  channel_rate
        self.mbs = self.delta*self.channel_rate
        self.used_mbs = 0
        self.num_users= num_users
        self.zois_list = []
        self.num_zois = num_zois
        self.tracesDic = OrderedDict()
        self.long_tracesDic = OrderedDict()
        self.attempts = 0
        self.connection_duration_list = OrderedDict()
        self.connection_location_list = OrderedDict()
        self.list_of_tuples_pos = []
        self.algorithm = algorithm
        self.city = None
        self.max_memory = max_memory
        self.max_time_elapsed = max_time_elpased
        self.inside_anchorzone = []
        self.beta = 0.8
        self.alpha = 0.5
        self.gamma = gamma
        self.rho = 0.333
        self.sigma = 0.333
        self.tau = 0.333
        self.statis = statis

        # If we only define 1 zoi we assume it is going to be located in the center of the scenario
        if self.num_zois == 1:
            zoi = Zoi(0,0,0,self)
            self.zois_list.append(zoi)

        # If we define more than one zoi, we should know if they are going to be based on map points or random uniform distribution
        if self.num_zois > 1:
            # In case we are running simulations based on maps points
            if traces_folder != "none":
                if traces_folder == "Rome":
                    self.city = "Rome"
                if traces_folder == "SanFrancisco":
                    self.city = "SanFrancisco"
                if traces_folder == "Luxembourg":
                    self.city = "Luxembourg"
                if traces_folder != "SanFrancisco" and traces_folder != "Rome" and traces_folder != "Luxembourg":
                    self.city="Paderborn"

                f=open('traces/POIS/'+self.city+'-POI-0.wkt',"r")
                lines=f.readlines()
                # First we read the points from the file
                for line in lines:
                    if line.startswith("POINT"):
                        num = re.findall(r'\d+(?:\.\d*)?', line)
                        numbers = [] 
                        numbers.append(float(num[0]))   
                        if self.city == 'SanFrancisco':
                            numbers.append(-float(num[1]))
                        else:
                            numbers.append(float(num[1]))

                        self.list_of_tuples_pos.append(numbers)
                        break

                f=open('traces/POIS/'+self.city+'-POI-1.wkt',"r")
                lines=f.readlines()
                # First we read the points from the file
                for line in lines:
                    if line.startswith("POINT"):
                        num = re.findall(r'\d+(?:\.\d*)?', line)
                        numbers = [] 
                        numbers.append(float(num[0]))
                        if self.city == 'SanFrancisco':
                            numbers.append(-float(num[1]))
                        else:
                            numbers.append(float(num[1]))

                        self.list_of_tuples_pos.append(numbers)
                        break 

                print('POINTS ', self.list_of_tuples_pos)
                # Second, we create the zois according to the points
                for i in range(0,len(self.list_of_tuples_pos)):
                    zoi = Zoi(i, self.list_of_tuples_pos[i][0],self.list_of_tuples_pos[i][1],self)
                    self.zois_list.append(zoi)

            
            # In case we are running simulations with zois in random positions within the scenario
            else:
                for i in range(0,self.num_zois):
                    zoi = Zoi(i, np.random.uniform(-self.max_area + self.radius_of_replication, self.max_area - self.radius_of_replication),
                    np.random.uniform(-self.max_area + self.radius_of_replication, self.max_area - self.radius_of_replication),self)
                    self.zois_list.append(zoi)

        # self.displayScenario()

    def displayScenario(self):
        print("Radius of interest : ", self.radius_of_interest,  ", Radius of replication: ", self.radius_of_replication, 
              ", Max area: ", self.max_area, ", Min speed: ", self.min_speed, 
              ", Max speed: ", self.max_speed, ", Max pause: ", self.max_pause, ", Min pause: ", self.max_pause, ", Delta: ", self.delta, 
              ", Radious of tx: ", self.radius_of_tx, ", Mbs: ", self.mbs, ", Used Mbs: ", self.used_mbs, 
              ", Channel rate: ", self.channel_rate, ", ZOIS: ", self.num_zois)


    # Traces parser for each scenario, we parse the traces after the scenario creation, depending on which folder (map) and file (specific traces for a given seed in that map)
    def parsePaderbornTraces(self, folder, file):
        self.num_users=51
        f=open('traces/' + folder + '/'+ file +'_MovementNs2Report.txt',"r")
        lines=f.readlines()
        count = 0
        for line in lines:
            lp = line.split()
            if "at" not in line: 
                node = int(line[line.find("(")+1:line.find(")")])
                if "X_" in line:
                    x = float(lp[3])
                if "Y_" in line:
                    y = float(lp[3])
                time = int(0)
                speed = float(0)
                count += 1
            else:
                count = 2
                node = int(line[line.find("(")+1:line.find(")")])
                time = float(lp[2])
                time = int(time)
                x = float(lp[5])
                y = float(lp[6])
                speed = float(lp[7][:-1])

            # We add the line info to each node dictionary
            if count == 2:
                count = 0
                if node not in self.tracesDic:
                    self.tracesDic[node] = OrderedDict()
                    self.tracesDic[node][time] = [x,y,speed]
                    # only for predict
                    self.long_tracesDic[node] = OrderedDict()
                    self.long_tracesDic[node][time] = [x,y,speed]

                    x = self.tracesDic[node].items()[0][1][0]
                    y = self.tracesDic[node].items()[0][1][1] 
                    user = User(node,x,y, self,self.max_memory,self.max_time_elapsed)
                    self.usr_list.append(user)
                    
                    
                else:
                    self.tracesDic[node][time] = [x,y,speed]
                    # only for predict
                    self.long_tracesDic[node][time] = [x,y,speed]


        self.num_users = len(self.tracesDic)
        print("nodos-->",self.num_users)

        for user in self.usr_list:
            user.predict(0)
            user.rz_visits_info.append(user.myFuture[0])
           
    # Traces parser for each scenario, we parse the traces after the scenario creation, depending on which folder (map) and file (specific traces for a given seed in that map)
    def parseRomaTraces(self, folder, file,dias):
        replacementDicc = OrderedDict()
        f=open('traces/' + folder + '/'+ file +'_Rome.txt',"r")
        lines=f.readlines()
        for line in lines:
            lp = line.split(';')
            node = lp[0]
            time = lp[1].split('-')
            time = time[2].split(':')
            daysHours = time[0].split(' ')
            days = ((int(daysHours[0])-1)*24)*3600
            hours = int(daysHours[1])*3600
            minutes = int(time[1])*60
            if "." in time[2]:
                seconds = int(time[2].split('.')[0])
            else:
                seconds = int(time[2].split('+')[0])

            totalSeconds = days+hours+minutes+seconds
            time = int(totalSeconds)

            coordinates = re.findall("\d+\.\d+", lp[2])
            x = float(coordinates[0])
            y = float(coordinates[1])

            # We add the line info to each node dictionary
            if node not in replacementDicc:
                replacementDicc[node] = OrderedDict()
            replacementDicc[node][time] = [x,y]


        nodes_counter=0
        for key,value in replacementDicc.items():
            self.long_tracesDic[nodes_counter] = OrderedDict()
            self.long_tracesDic[nodes_counter] = value
            nodes_counter +=1 

        self.num_users = len(self.long_tracesDic)



    def cutTracesDict(self, ini, end):
        self.tracesDic = OrderedDict()
        self.tracesDic = OrderedDict()
        for key,value in self.long_tracesDic.items():
            count = 0
            for k,v in value.items():
                if k>=ini and k<=end:
                    if count == 0:
                        self.tracesDic[key] = OrderedDict()
                        count = 1
                    self.tracesDic[key][k] = v



    def parseSanFranciscoTraces(self, folder):
        counter_users = 0
        replacementDicc= OrderedDict()
        replacementDicc2= OrderedDict()

        folder = 'traces/' + folder
        for filename in os.listdir(folder):
            f=open(folder + '/'+ filename,"r")
            lines=f.readlines()
            for line in lines:
                node = counter_users
                lp = line.split(' ')
                x = float(lp[0])
                y = float(lp[1])
                time = int(lp[3])

                given_date_format = datetime.fromtimestamp(time).strftime('%d-%m-%Y %H:%M:%S')
                given_date = datetime.strptime(given_date_format, '%d-%m-%Y %H:%M:%S')

                fix_starting_date_format = datetime.fromtimestamp(1211018400).strftime('%d-%m-%Y %H:%M:%S')
                fix_starting_date = datetime.strptime(fix_starting_date_format, '%d-%m-%Y %H:%M:%S')

                time = given_date-fix_starting_date
                time = int(time.total_seconds())

                 # We add the line info to each node dictionary
                    
                if time < self.num_slots:
                    if node not in replacementDicc:
                        replacementDicc[node] = OrderedDict()
                        self.long_tracesDic[node] = OrderedDict()
                    replacementDicc[node][time] = [x,y]

            if node in replacementDicc.keys():
                for k,v in reversed(replacementDicc[node].items()):
                    self.long_tracesDic[node][k] = v

                counter_users += 1

        self.num_users = counter_users

    def addRemoveNodes(self,c): 
        for k in self.tracesDic.keys():
            if len(self.long_tracesDic[k].keys())>0 and c in self.long_tracesDic[k].keys():
                if self.long_tracesDic[k].keys()[0] == c:
                    x = self.long_tracesDic[k].items()[0][1][0]
                    y = self.long_tracesDic[k].items()[0][1][1] 
                    user = User(k,x,y, self,self.max_memory,self.max_time_elapsed)
                    self.usr_list.append(user)
                    user.predict(c)
                    user.rz_visits_info.append(user.myFuture[c])


                if self.long_tracesDic[k].keys()[-1] == c:
                    for u in self.usr_list:
                        if k == u.id:
                            self.usr_list.remove(u)  

                if  self.long_tracesDic[k].keys()[0] != c and self.long_tracesDic[k].keys()[-1] != c:
                    actual_index = self.long_tracesDic[k].keys().index(c)
                    previous_key = list(self.long_tracesDic[k].keys())[actual_index-1]
                    if (c - previous_key) > 300:
                        x = self.long_tracesDic[k].items()[0][1][0]
                        y = self.long_tracesDic[k].items()[0][1][1] 

                        for user in self.helper_usr_list:
                            if user.id == k:
                                self.usr_list.append(user)
                                self.helper_usr_list.remove(user)
                                user.rz_visits_info.append(user.myFuture[c])


                    actual_index = self.long_tracesDic[k].keys().index(c)
                    next_key = list(self.long_tracesDic[k].keys())[actual_index+1]
                    if (next_key - c) > 300:
                        for u in self.usr_list:
                            if k == u.id:
                                self.helper_usr_list.append(u)
                                self.usr_list.remove(u) 

            if c not in self.long_tracesDic[k].keys() and (c-1) in self.long_tracesDic[k].keys() and self.long_tracesDic[k].keys()[-1] != (c-1):
                previous_index = self.long_tracesDic[k].keys().index(c-1)
                print(len(self.long_tracesDic[k]), previous_index + 1)
                next_key = list(self.long_tracesDic[k].keys())[previous_index+1]
                if (next_key - c) > 300:
                    for u in self.usr_list:
                        if k == u.id:
                            self.helper_usr_list.append(u)
                            self.usr_list.remove(u) 


    def parseLuxembourgTraces(self, folder,file):
        with open('traces/' + folder + '/tracesLux-'+file+'.json', 'r') as fp:
                data = json.load(fp, object_pairs_hook=OrderedDict)
            
        for k,v in data.items():
            self.long_tracesDic[int(k)] = OrderedDict()
            for key,value in v.items():
                self.long_tracesDic[int(k)][int(key)]=[]
                for coord in value:
                    self.long_tracesDic[int(k)][int(key)].append(float(coord))
       
        self.num_users = len(self.long_tracesDic)
