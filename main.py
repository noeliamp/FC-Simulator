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
from  shutil import copyfile

t0 = time.time()
uid = base64.urlsafe_b64encode(hashlib.md5(os.urandom(128)).digest())[:8]
with open('input.json') as f:
    data = json.load(f)


num_sim = data["num_sim"]                               # number of simulations
num_slots = data["num_slots"]                           # number of repetitions in one simulation
density_users = data["num_users"]
density_zois = data["num_zois"]
num_users_distribution = data["num_users_distribution"] # number of users distribution
num_zois_distribution = data["num_zois_distribution"]   # number of zois distribution
radius_of_tx = data["radius_of_tx"]                     # area to look for neigbors (dependent on contact range)
max_area = data["max_area_squared"]                     # outer zone - max area size
radius_of_interest = data["radius_of_interest"]         # inner zone - interest
radius_of_replication = data["radius_of_replication"]   # second zone - replication
radius_of_persistence = data["radius_of_persistence"]   # third zone - persistence
min_speed = data["min_speed"]
max_speed = data["max_speed"]
min_pause = data["min_pause"]
max_pause = data["max_pause"]
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
num_content_per_zoi = data["num_content_per_zoi"]

# different content size during simulations
# content_size_list = [100,9310441.379,18620782.76,27931124.14,37241465.52,46551806.9,55862148.28,65172489.66,74482831.03,83793172.41,93103513.79,102413855.2,111724196.6,121034537.9,130344879.3,139655220.7,148965562.1,158275903.4,167586244.8,176896586.2,186206927.6,195517269,204827610.3,214137951.7,223448293.1,232758634.5,242068975.9,251379317.2,260689658.6,270000000]
content_size_list = [1000,100000,1000000,100000000,80000]

seed_list = [15482669,15482681,15482683,15482711,15482729,15482941,15482947,15482977,15482993,15483023,15483029,15483067,15483077,15483079,15483089,15483101,15483103,15482743,15482771,15482773,15482783,15482807,15482809,15482827,15482851,15482861,15482893,15482911,15482917,15482923]
uid = str(max_speed) + "-" + str(radius_of_tx) + "-" + str(radius_of_replication) + "-" + str(radius_of_persistence) + "-"+ str(uid) 
os.mkdir(uid)
print(uid)

avb_per_sim = []
list_of_lists_avg_10 = []
avb_per_sim_per_slot= []

zoi_counter= OrderedDict()
per_counter = OrderedDict()
rep_counter= OrderedDict()
zoi_users_counter = OrderedDict()
per_users_counter = OrderedDict()
rep_users_counter = OrderedDict()
contacts_per_slot_per_user= OrderedDict()

content_size_index = 4

copyfile('input.json', str(uid)+'/input.json') # Copy the corresponding input file into the folder
################## Loop per simulation
for s in range(0,num_sim):
    # np.random.seed(seed_list[s])
    print("SIMULATION--> ", s)
    print("content size ", content_size_list[content_size_index])
    # progress bar
    bar = progressbar.ProgressBar(maxval=num_slots, \
        widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    orig_stdout = sys.stdout
    # f = open(os.devnull, 'w')
    f = open(str(uid)+'/out-'+str(s)+'.txt', 'w')
    sys.stdout = f      


    usr_list = []        # list of users in the entire scenario

    # This creates N objects of User class
    if num_users_distribution == "poisson":
        num_users = np.random.poisson(density_users)
        print("Number of users:", num_users)
    else:
        num_users=density_users
        print("Number of users:", num_users)

    print("Content size: ", content_size_list[content_size_index])

    # This creates N objects of ZOI class
    if num_zois_distribution == "poisson":
        num_zois = np.random.poisson(density_zois)
        print("Number of zois:", num_zois)
    else:
        num_zois=density_zois
        print("Number of zois:", num_zois)


    # CREATION OF SCENARIO With num_zois number of zois
    scenario = Scenario(radius_of_interest, radius_of_replication, radius_of_persistence, max_area,speed_distribution,pause_distribution,min_pause,max_pause, 
    min_speed,max_speed,delta,radius_of_tx,channel_rate,num_users,min_flight_length, max_flight_length,flight_length_distribution,hand_shake,num_zois)
    
    # CREATION OF ONE CONTENT PER ZOI and initializing counters of nodes with and without content per ZOI
    for z in scenario.zois_list:
        msg = Message(uuid.uuid4(),content_size_list[content_size_index],z)
        z.content_list.append(msg)
        zoi_counter[z]= 0
        per_counter[z] = 0
        rep_counter[z]= 0
        zoi_users_counter[z] = 0
        per_users_counter[z] = 0
        rep_users_counter[z] = 0   

    # CREATION OF USERS
    for i in range(0,num_users):
        user = User(i,np.random.uniform(-max_area, max_area),np.random.uniform(-max_area, max_area), scenario,max_memory)
        # add the content to each user according to the ZOIs that they belong to
        for z in user.zones.keys():
            # to compute the first availability (if node is not out it will have the message for sure)
            if user.zones[z] == "interest":
                user.messages_list.extend(z.content_list)
                zoi_users_counter[z] += 1
                zoi_counter[z] += 1
            
            if user.zones[z] == "replication":
                user.messages_list.extend(z.content_list)
                rep_users_counter[z] += 1
                rep_counter[z] += 1
            
            if user.zones[z] == "persistence":
                # user.messages_list.extend(z.content_list)
                per_users_counter[z] += 1
                # per_counter += 1
            
            # we are not counting nodes that are out of every zoi  

        # After creating a user, adding the messages according to the zones it belongs to and setting availability counters, 
        # now we set the amount of memory used by the node according to the messages that were included in its list.
        for m in user.messages_list:
            user.used_memory += m.size                     
    
        usr_list.append(user)


    # add the list of users to every scenario
    scenario.usr_list = usr_list

    slots = []
    zoi = []
    rep = []
    per = []
    zoi_users = []
    rep_users = []
    per_users = []
    out_users = []
    failures = []
    attempts = []
    a_list = []
    a_per_zoi = OrderedDict()
    availability_per_zoi = OrderedDict()

    print("zoi_users_counter ",zoi_users_counter.values(),zoi_counter.values())
    print("rep_users_counter ",rep_users_counter.values(),rep_counter.values())
    print("per_users_counter ",per_users_counter.values(),per_counter.values())
    # Computing availability per ZOI
    for z in scenario.zois_list:
        if (zoi_users_counter[z]+rep_users_counter[z]) == 0:
            av = 0
        else:
            av = (zoi_counter[z] + rep_counter[z])/(zoi_users_counter[z]+rep_users_counter[z])

        a_per_zoi[z] = av
        availability_per_zoi[z] = []


    a = np.average(a_per_zoi.values())

    print("per zoi availability: ", a_per_zoi.values())
    print("this availability: " , a)


    a_avg_list = []
    availabilities_list_per_slot = []
    # a_avg_list_squared = []
    num_slots_counter = 0
    aux = 0
    th=0.4
    c = 0
    
    ################## Loop per slot into a simulation
    while c < num_slots and a > 0:
    # aux < th:
        for z in scenario.zois_list:
            zoi_counter[z] = 0
            per_counter[z] = 0
            rep_counter[z]= 0
            zoi_users_counter[z] = 0
            per_users_counter[z] = 0
            rep_users_counter[z] = 0

        CI = 0
        failures_counter = 0
        attempts_counter = 0
        
        bar.update(c+1)
        slots.append(c)
        num_slots_counter += 1
        c += 1

        # shuffle users lists
        np.random.shuffle(scenario.usr_list)

        # Run mobility for every slot           
        # Nobody should be BUSY at the beggining of a slot (busy means that the node has had a connection already in the current slot, so it cannot have another one)
        # Move every pedestrians once
        for j in range(0,num_users):
            scenario.usr_list[j].busy = False
            scenario.usr_list[j].randomDirection()

        # Run contacts for every slot after mobility. Attempts and failures are set to 0 at the beggining of every slot.   
        for k in range(0,num_users):
            scenario.usr_list[k].failures_counter = 0
            scenario.usr_list[k].attempts_counter = 0

            # run users contact
            scenario.usr_list[k].contacts_per_slot[c] = []
            scenario.usr_list[k].userContact(c)

            failures_counter += scenario.usr_list[k].failures_counter
            attempts_counter += scenario.usr_list[k].attempts_counter
     

        # After moving the node and exchanging content, check to which zone it belongs to increase the right counter
        for j in range(0,num_users):
            for z in scenario.usr_list[j].zones.keys():
                if scenario.usr_list[j].zones[z] == "interest":
                    zoi_users_counter[z] += 1
                    if len(scenario.usr_list[j].messages_list)>0:
                        if any(x.zoi == z for x in scenario.usr_list[j].messages_list):
                            zoi_counter[z] += 1
                
                if scenario.usr_list[j].zones[z] == "replication":
                    rep_users_counter[z] += 1
                    if len(scenario.usr_list[j].messages_list)>0:
                        if any(x.zoi == z for x in scenario.usr_list[j].messages_list):
                            rep_counter[z] += 1
                
                if scenario.usr_list[j].zones[z] == "persistence":
                    per_users_counter[z] += 1
                    if len(scenario.usr_list[j].messages_list)>0:
                        if any(x.zoi == z for x in scenario.usr_list[j].messages_list):
                            per_counter[z] += 1
                
                # we are not counting the nodes that are out of every zoi

        ################################## Dump data per slot in a file ############################################
        
        zoi.append(zoi_counter[z])
        rep.append(rep_counter[z])
        per.append(per_counter[z])
        zoi_users.append(zoi_users_counter[z])
        rep_users.append(rep_users_counter[z])
        per_users.append(per_users_counter[z])
        failures.append(failures_counter)
        attempts.append(attempts_counter)

        print("zoi_users_counter ",zoi_users_counter.values(),zoi_counter.values())
        print("rep_users_counter ",rep_users_counter.values(),rep_counter.values())
        print("per_users_counter ",per_users_counter.values(),per_counter.values())

        # we add the current slot availability to the list a_list
        for z in scenario.zois_list:
            if (zoi_users_counter[z] + rep_users_counter[z]) == 0:
                av = 0
            else:
                av = (zoi_counter[z] + rep_counter[z])/(zoi_users_counter[z]+rep_users_counter[z])
            a_per_zoi[z] = av
            availability_per_zoi[z].append(av)

        a = np.average(a_per_zoi.values())
        a_list.append(a)
        availabilities_list_per_slot.append(a)

        print("per zoi availability: ", a_per_zoi.values())
        print("this availability: " , a)

        if num_slots_counter == 10:
            # Once we reach the desired number of slots per window, we compute the average of the availabilities for that window
            avg = np.average(a_list)
            print("a_list: ", a_list)
            a_avg_list.append(avg)
            print("avg: ", avg)
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
    
    # Add the average of the availability averages in this simulation to the final list of availabilities (one point per simulation)
    avb_per_sim.append(np.average(a_avg_list))
    list_of_lists_avg_10.append(a_avg_list)
    avb_per_sim_per_slot.append(availabilities_list_per_slot)

    # At the end of every simulation we need to close connections and add it to the list of connection durations
    for k in range(0,num_users):
        if scenario.usr_list[k].ongoing_conn == True:
            scenario.usr_list[k].connection_duration_list.append(scenario.usr_list[k].connection_duration)
            scenario.usr_list[k].successes_list_A.append(scenario.usr_list[k].suc)
            scenario.usr_list[k].successes_list_B.append(scenario.usr_list[k].prev_peer.suc)
            scenario.usr_list[k].ex_list_print_A.append(len(scenario.usr_list[k].exchange_list))
            scenario.usr_list[k].ex_list_print_B.append(len(scenario.usr_list[k].prev_peer.exchange_list))
            scenario.usr_list[k].ongoing_conn = False
            scenario.usr_list[k].prev_peer.ongoing_conn = False
        
        
    for u in scenario.usr_list:
        contacts_per_slot_per_user[u.id] = u.contacts_per_slot



    ###################### Functions to dump data per simulation #########################
    dump = Dump(scenario,uid,s)
    dump.userLastPosition()
    dump.statisticsList(slots, zoi_users, zoi, rep_users, rep, per_users, per,failures, attempts)
    dump.connectionDurationAndMore(contacts_per_slot_per_user)
    dump.availabilityPerZoi(availability_per_zoi.values())
    
    ########################## End of printing in simulation ##############################
    sys.stdout = orig_stdout
    f.close()
    bar.finish()
    t1 = time.time()
    print ("Total time running: %s minutes \n" % str((t1-t0)/60))

########################## End of simulations, print and dump relevant final info ##############################

print("last availability: ", avb_per_sim)
print("flight length: ", scenario.flight_length_distribution)
print("flight : ", scenario.usr_list[0].flight_length)
print("speed : ", scenario.usr_list[0].speed)

np.savetxt(str(uid)+'/availability_points.txt', avb_per_sim , fmt="%1.3f")

outfile = open(str(uid)+'/list_of_averages.txt', 'w')
for result in list_of_lists_avg_10:
    outfile.writelines(str(result))
    outfile.write('\n')
outfile.close()

outfile = open(str(uid)+'/availability_per_slot_per_sim.txt', 'w')
for result in avb_per_sim_per_slot:
    outfile.writelines(str(result))
    outfile.write('\n')
outfile.close()