from __future__ import division
from User import User
from Dump import Dump
from Message import Message
from Scenario import Scenario
import numpy as np
import json
from collections import OrderedDict
import sys, os
from random import shuffle
import uuid
import progressbar
from time import sleep
import time

orig_stdout = sys.stdout
# f = open(os.devnull, 'w')
f = open('out.txt', 'w')
sys.stdout = f

# file = open('dump.txt', 'w') 

t0 = time.time()

with open('input.json') as f:
    data = json.load(f)

num_sim = data["num_sim"]                               # number of simulations
num_slots = data["num_slots"]                           # number of repetitions in one simulation
density = data["num_users"]
num_users_distribution = data["num_users_distribution"] # number of users distribution
radius_of_tx = data["radius_of_tx"]                     # area to look for neigbors (dependent on contact range)
max_area = data["max_area_squared"]                     # outer zone - max area size
radius_of_interest = data["radius_of_interest"]         # inner zone - interest
radius_of_replication = data["radius_of_replication"]   # second zone - replication
radius_of_persistence = data["radius_of_persistence"]   # third zone - persistence
min_speed = data["min_speed"]
max_speed = data["max_speed"]
min_pause = data["min_pause"]
max_pause = data["max_pause"]
user_generation_distribution = data["user_generation_distribution"]
speed_distribution = data["speed_distribution"]
pause_distribution = data["pause_distribution"]
delta = data["delta"]                                   # time per slot
channel_rate = data["channel_rate"]
max_memory = data["max_memory"]                         # max memory allowed per user device
max_message_size = data["max_message_size"]
min_flight_length = data["min_flight_length"]
max_flight_length = data["max_flight_length"]
flight_length_distribution = data["flight_length_distribution"]
hand_shake = data["hand_shake"]
window_size = data["window_size"]

    

usrList = []                                            # list of users
statusList = ['available', 'infected']

# This creates N objects of User class
if num_users_distribution == "poisson":
    num_users = np.random.poisson(density)
    print("Number of users:", num_users)
else:
    num_users=density

# progress bar
bar = progressbar.ProgressBar(maxval=num_slots, \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
bar.start()

# This creates the scenario defined in the input script
scenario = Scenario(radius_of_interest, radius_of_replication, radius_of_persistence, max_area, user_generation_distribution, speed_distribution,pause_distribution,
                    min_pause,max_pause, min_speed,max_speed,delta,radius_of_tx,usrList,channel_rate,num_users,min_flight_length,max_flight_length,
                    flight_length_distribution,hand_shake)

msg1 = Message(uuid.uuid4(),max_message_size)

for i in range(1,num_users+1):
    # waypoints are independently and identically distributed (i.i.d.) using a uniform random
    # distribution over the system space.
    # The values for the pause time are chosen from a bounded random distribution in the interval [0, tp,max] with tp,max < inf. 
    # In general the speed is also chosen from a random distribution within the interval [vmin, vmax] with vmin > 0 and vmax < inf.   

    # add the same message to all the users
    user = User(i,np.random.uniform(-max_area, max_area),np.random.uniform(-max_area, max_area), scenario,max_memory,max_message_size)
    if user.zone != "outer":
        user.messages_list.append(msg1)
        user.used_memory = msg1.size
    
    usrList.append(user)

# add the new list of users to the scenario
scenario.usrList = usrList
slots = []
zoi = []
rep = []
per = []
out = [] 
zoi_users = []
rep_users = []
per_users = []
out_users = []
failures = []
attempts = []
connection_duration_list = []
iHadMessage_list = []
a = 0
a_list = []
a_avg_list = []
a_avg_list_squared = []
num_slots_counter = 0
aux = 0
th=0.4
c = 0

# for i in range(0,num_slots):
while c < num_slots and aux < th:
    CI = 0
    a_list = []
    failures_counter = 0
    attempts_counter = 0
    iHadMessage_counter = 0
    bar.update(c+1)
    sleep(0.1)
    slots.append(c)
    num_slots_counter = num_slots_counter + 1
    c = c + 1

    # Run mobility for every slot
    # print ('\n Lets run mobility slot: %d' % i)
    # Nobody is BUSY at the beggining of a slot
    for l in range(0,num_users):
        scenario.usrList[l].buys = False
    # Move every pedestrian once
    for j in range(0,num_users):
        scenario.usrList[j].randomDirection()


    # Run contacts for every slot after mobility, at the beggining of every slot every user is available --> busy = Flase
    # print ('\n Lets run contacts slot: %d' % i)
    for k in range(0,num_users):
        scenario.usrList[k].busy = False

    # suffle users lists
    shuffle(scenario.usrList)
    for k in range(0,num_users):
        scenario.usrList[k].failures_counter = 0
        scenario.usrList[k].attempts_counter = 0

        # run users contact
        scenario.usrList[k].userContact()

        failures_counter = failures_counter + scenario.usrList[k].failures_counter
        attempts_counter = attempts_counter +  scenario.usrList[k].attempts_counter



    ################################## Dump data per slot in a file ############################################
    
    zoi_counter= 0
    per_counter = 0
    rep_counter= 0
    out_counter = 0
    zoi_users_counter = 0
    per_users_counter = 0
    rep_users_counter = 0
    out_users_counter = 0
    iHadMessage_counter = 0

    for k in range(0,num_users):
        if scenario.usrList[k].zone == "interest":
            zoi_users_counter = zoi_users_counter + 1
            if len(scenario.usrList[k].messages_list) == 1:
                zoi_counter = zoi_counter + 1
        
    for k in range(0,num_users):
        if scenario.usrList[k].zone == "replication":
            rep_users_counter = rep_users_counter + 1
            if len(scenario.usrList[k].messages_list) == 1:
                rep_counter = rep_counter + 1
        
    for k in range(0,num_users):
        if scenario.usrList[k].zone == "persistence":
            per_users_counter = per_users_counter + 1
            if len(scenario.usrList[k].messages_list) == 1:
                per_counter = per_counter + 1
        
    for k in range(0,num_users):
        if scenario.usrList[k].zone == "outer":
            out_users_counter = out_users_counter + 1
            if len(scenario.usrList[k].messages_list) == 1:
                out_counter = out_counter + 1

    for k in range(0,num_users):
        if scenario.usrList[k].iHadMessage == True:
            iHadMessage_counter = iHadMessage_counter + 1
            scenario.usrList[k].iHadMessage = False
    
    zoi.append(zoi_counter)
    rep.append(rep_counter)
    per.append(per_counter)
    out.append(out_counter)
    zoi_users.append(zoi_users_counter)
    rep_users.append(rep_users_counter)
    per_users.append(per_users_counter)
    out_users.append(out_users_counter)
    failures.append(failures_counter)
    attempts.append(attempts_counter)
    iHadMessage_list.append(iHadMessage_counter)

    # we add the current slot availability to the list a_list
    a = (zoi_counter + rep_counter + per_counter)/(zoi_users_counter+rep_users_counter+per_users_counter)
    a_list.append(a)
    print(a)

    if num_slots_counter == window_size/delta:
        # Once we reach the desired number of slots per window, we compute the average of the availabilities for that window
        avg = sum(a_list)/len(a_list)
        a_avg_list.append(avg)
        a_avg_list_squared.append(np.power(avg,2))
        # compute the standard deviation up to that window
        num = sum(a_avg_list_squared)-(np.power(sum(a_avg_list),2))/len(a_avg_list)
        den = len(a_avg_list)-1   
        if den != 0:
            sd = np.sqrt(num/den)
        else: 
            sd = 0

        # compute the confidence interval up to this window
        min = a - ((1.96 * sd)/np.sqrt(len(a_avg_list)))
        max = a + ((1.96 * sd)/np.sqrt(len(a_avg_list)))
        CI = max - min
        mi = sum(a_avg_list)/len(a_avg_list)
        # variable to check if next point is smaller than a threshold (comparison in the while loop)
        aux = CI/mi

        print("avrg: ", avg, " sd: ", sd, " aux: ", aux)
        num_slots_counter = 0
        a_list = []

for k in range(0,num_users):
    if scenario.usrList[k].ongoing_conn == True:
        scenario.usrList[k].connection_duration_list.append(scenario.usrList[k].connection_duration)
        scenario.usrList[k].ongoing_conn = False
        scenario.usrList[k].prev_peer.ongoing_conn = False

avg_used_mbs_per_node = sum(scenario.used_mbs_per_slot)/len(scenario.used_mbs_per_slot)
print(scenario.used_mbs_per_slot)
print(len(scenario.used_mbs_per_slot),num_slots)
print(avg_used_mbs_per_node)
print(msg1.size)
np.savetxt('dump-30-100-200-250.txt', np.column_stack((slots, zoi_users, zoi, rep_users, rep, per_users, per, out_users, out,failures, attempts,iHadMessage_list)), 
fmt="%i %i %i %i %i %i %i %i %i %i %i %i")


for k in range(0,num_users):
    connection_duration_list.append(scenario.usrList[k].connection_duration_list)

flat_list = [item for sublist in connection_duration_list for item in sublist]

np.savetxt('connection-duration-list.txt', flat_list , fmt="%i")

###################### SELECT A FUNCTION TO DUMP DATA ###########################
dump = Dump(scenario)
dump.userLastPosition()
# dump.infoPerZone()

########################## End of printing ######################################
sys.stdout = orig_stdout
f.close()

bar.finish()
t1 = time.time()
print("Lenght of connection duration list: %d" % len(flat_list))
print ("Total time running: %s minutes" % str((t1-t0)/60))