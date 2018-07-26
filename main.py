from __future__ import division
from User import User
from Dump import Dump
from Message import Message
from Scenario import Scenario
import numpy as np
import json
from collections import OrderedDict
import sys, os
import uuid
import progressbar
from time import sleep
import time
import uuid
import os
import base64
import hashlib

t0 = time.time()
uid = base64.urlsafe_b64encode(hashlib.md5(os.urandom(128)).digest())[:8]
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
num_scenarios = data["num_scenarios"]
num_content = data["num_content"]

# different content size during simulations
content_size_list = [100,9310441.379,18620782.76,27931124.14,37241465.52,46551806.9,55862148.28,65172489.66,74482831.03,83793172.41,93103513.79,102413855.2,111724196.6,121034537.9,130344879.3,139655220.7,148965562.1,158275903.4,167586244.8,176896586.2,186206927.6,195517269,204827610.3,214137951.7,223448293.1,232758634.5,242068975.9,251379317.2,260689658.6,270000000]
seed_list = [15482669,15482681,15482683,15482711,15482729,15482941,15482947,15482977,15482993,15483023,15483029,15483067,15483077,15483079,15483089,15483101,15483103,15482743,15482771,15482773,15482783,15482807,15482809,15482827,15482851,15482861,15482893,15482911,15482917,15482923]
uid = str(max_speed) + "-" + str(radius_of_tx) + "-" + str(radius_of_replication) + "-" + str(radius_of_persistence) + "-"+ str(uid) 
os.mkdir(uid)
print(uid)

avb_per_sim = []
list_of_lists_avg_10 = []
zoi_counter= 0
per_counter = 0
rep_counter= 0
out_counter = 0
zoi_users_counter = 0
per_users_counter = 0
rep_users_counter = 0
out_users_counter = 0

for s in range(0,num_sim):
    # np.random.seed(seed_list[s])
    print("SIMULATION--> ", s)
    print("content size ", content_size_list[s])
    # progress bar
    bar = progressbar.ProgressBar(maxval=num_slots, \
        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    orig_stdout = sys.stdout
    # f = open(os.devnull, 'w')
    f = open(str(uid)+'/out-'+str(s)+'.txt', 'w')
    sys.stdout = f      

    usr_list = []        # list of users
    scenarios_list = []  # list of scenarios

    # This creates N objects of User class
    if num_users_distribution == "poisson":
        num_users = np.random.poisson(density)
        print("Number of users:", num_users)
    else:
        num_users=density
        print("Number of users:", num_users)


    # CREATION OF SCENARIOS
    for ns in range(1,num_scenarios+1):
        scenario = Scenario(s,radius_of_interest, radius_of_replication, radius_of_persistence, max_area, user_generation_distribution, speed_distribution,pause_distribution,
                            min_pause,max_pause, min_speed,max_speed,delta,radius_of_tx,usr_list,channel_rate,num_users,min_flight_length,max_flight_length,
                            flight_length_distribution,hand_shake)
        # CREATION OF CONTENT
        # msg1 = Message(uuid.uuid4(),max_message_size)
        for c in range(1,num_content+1):
            msg1 = Message(uuid.uuid4(),content_size_list[s])

        # CREATION OF USERS
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
            # to compute the first availability
            if user.zone == "interest":
                zoi_users_counter += 1
                if len(user.messages_list) == 1:
                    zoi_counter += 1
            
            if user.zone == "replication":
                rep_users_counter += 1
                if len(user.messages_list) == 1:
                    rep_counter += 1
            
            if user.zone == "persistence":
                per_users_counter += 1
                if len(user.messages_list) == 1:
                    per_counter += 1
            
            if user.zone == "out":
                out_users_counter += 1
                if len(user.messages_list) == 1:
                    out_counter += 1
                        
        
            usr_list.append(user)

      
        # add the list of users to every scenario
        scenario.usr_list = usr_list
        scenarios_list.append(scenario)



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
    a_list = []
    if (zoi_users_counter+rep_users_counter) == 0:
        a = 0
    else:
        a = (zoi_counter + rep_counter)/(zoi_users_counter+rep_users_counter)
    a_avg_list = []
    a_avg_list_squared = []
    num_slots_counter = 0
    aux = 0
    th=0.4
    c = 0
    
    # for i in range(0,num_slots):
    while c < num_slots and a > 0:
    # aux < th:
        zoi_counter= 0
        per_counter = 0
        rep_counter= 0
        out_counter = 0
        zoi_users_counter = 0
        per_users_counter = 0
        rep_users_counter = 0
        out_users_counter = 0
        CI = 0
        a_list = []
        failures_counter = 0
        attempts_counter = 0
        
        bar.update(c+1)
        # sleep(0.1)
        slots.append(c)
        num_slots_counter += 1
        c += 1

        # Run mobility for every slot
        # print ('\n Lets run mobility slot: %d' % i)
        # Nobody is BUSY at the beggining of a slot
        # Move every pedestrian once
        for j in range(0,num_users):
            scenario.usr_list[j].busy = False
            scenario.usr_list[j].randomDirection()
            # After moving, compute to which zone it belongs to increase the right counter
            if scenario.usr_list[j].zone == "interest":
                zoi_users_counter += 1
                if len(scenario.usr_list[j].messages_list) == 1:
                    zoi_counter += 1
            
            if scenario.usr_list[j].zone == "replication":
                rep_users_counter += 1
                if len(scenario.usr_list[j].messages_list) == 1:
                    rep_counter += 1
            
            if scenario.usr_list[j].zone == "persistence":
                per_users_counter += 1
                if len(scenario.usr_list[j].messages_list) == 1:
                    per_counter += 1
            
            if scenario.usr_list[j].zone == "outer":
                out_users_counter += 1
                if len(scenario.usr_list[j].messages_list) == 1:
                    out_counter += 1

        # Run contacts for every slot after mobility, at the beggining of every slot every user is available --> busy = Flase
        # print ('\n Lets run contacts slot: %d' % i)
        # shuffle users lists
        np.random.shuffle(scenario.usr_list)
        for k in range(0,num_users):
            scenario.usr_list[k].failures_counter = 0
            scenario.usr_list[k].attempts_counter = 0

            # run users contact
            scenario.usr_list[k].userContact()

            failures_counter += scenario.usr_list[k].failures_counter
            attempts_counter += scenario.usr_list[k].attempts_counter

        ################################## Dump data per slot in a file ############################################
        
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

        # we add the current slot availability to the list a_list
        if (zoi_users_counter+rep_users_counter) == 0:
            a = 0
        else:
            a = (zoi_counter + rep_counter)/(zoi_users_counter+rep_users_counter)
        a_list.append(a)

        if num_slots_counter == 10:
            # Once we reach the desired number of slots per window, we compute the average of the availabilities for that window
            avg = np.average(a_list)
            a_avg_list.append(avg)

            # compute the standard deviation up to that window

            # a_avg_list_squared.append(np.power(avg,2))
            # num = sum(a_avg_list_squared)-(np.power(sum(a_avg_list),2))/len(a_avg_list)
            # den = len(a_avg_list)-1   
            # if den != 0:
            #     sd = np.sqrt(num/den)
            # else: 
            #     sd = 0

            # # compute the confidence interval up to this window
            # min = a - ((1.96 * sd)/np.sqrt(len(a_avg_list)))
            # max = a + ((1.96 * sd)/np.sqrt(len(a_avg_list)))
            # CI = max - min
            # mi = sum(a_avg_list)/len(a_avg_list)
            # # variable to check if next point is smaller than a threshold (comparison in the while loop)
            # aux = CI/mi

            num_slots_counter = 0
            a_list = []
           
    for k in range(0,num_users):
        if scenario.usr_list[k].ongoing_conn == True:
            scenario.usr_list[k].connection_duration_list.append(scenario.usr_list[k].connection_duration)
            scenario.usr_list[k].ongoing_conn = False
            scenario.usr_list[k].prev_peer.ongoing_conn = False

    np.savetxt(str(uid)+'/dump-'+str(s)+'.txt', np.column_stack((slots, zoi_users, zoi, rep_users, rep, per_users, per, out_users, out,failures, attempts)), 
    fmt="%i %i %i %i %i %i %i %i %i %i %i")


    for k in range(0,num_users):
        connection_duration_list.append(scenario.usr_list[k].connection_duration_list)

    flat_list = [item for sublist in connection_duration_list for item in sublist]
    np.savetxt(str(uid)+'/connection-duration-list-'+str(s)+'.txt', flat_list , fmt="%i")

    # Add the average of the availability averages in this simulation to the final list of availabilities (one point per simulation)
    avb_per_sim.append(np.average(a_avg_list))
    list_of_lists_avg_10.append(a_avg_list)

    ###################### SELECT A FUNCTION TO DUMP DATA ###########################
    dump = Dump(scenario)
    dump.userLastPosition(uid)
    # dump.infoPerZone()

    ########################## End of printing ######################################
    sys.stdout = orig_stdout
    f.close()

    bar.finish()
    t1 = time.time()
    # print("Lenght of connection duration list: %d" % len(flat_list))
    print ("Total time running: %s minutes" % str((t1-t0)/60))

# print("list of averages: ", list_of_lists_avg_10)
print("availability: ", avb_per_sim)
np.savetxt(str(uid)+'/availability_points.txt', avb_per_sim , fmt="%1.3f")

outfile = open(str(uid)+'/list_of_averages.txt', 'w')
for result in list_of_lists_avg_10:
  outfile.writelines(str(result))
  outfile.write('\n')
outfile.close()

