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

# file_name = raw_input("Enter the configuration code: ")
# print("Configuration chosen, {}!".format(file_name))
# print('Number of arguments:', len(sys.argv), 'arguments.')
# print('Argument List:', str(sys.argv))
# print(type(sys.argv[1]), sys.argv[1])

file_name = str(sys.argv[1])
print('input-'+ file_name + '.json')

t0 = time.time()
uid = base64.urlsafe_b64encode(hashlib.md5(os.urandom(128)).digest())[:8]

with open('input-'+ file_name + '.json') as f:
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
if max_memory == "inf":
    max_memory = np.inf
max_message_size = data["max_message_size"]
min_message_size = data["min_message_size"]
content_size = np.random.uniform(max_message_size, min_message_size)
min_flight_length = data["min_flight_length"]
max_flight_length = data["max_flight_length"]
flight_length_distribution = data["flight_length_distribution"]
hand_shake = data["hand_shake"]
num_contents = data["num_contents"]
num_contents_node = data["num_contents_node"]


seed_list = [15482669,15482681,15482683,15482711,15482729,15482941,15482947,15482977,15482993,15483023,15483029,15483067,15483077,15483079,15483089,15483101,15483103,15482743,15482771,15482773,15482783,15482807,15482809,15482827,15482851,15482861,15482893,15482911,15482917,15482923]
uid =  str(file_name) + "-"+ str(uid) 
os.mkdir(uid)
print(uid)

# avb_per_sim = []
list_of_lists_avg_10 = []
avb_per_sim_per_slot= []

zoi_counter= OrderedDict()
per_counter = OrderedDict()
rep_counter= OrderedDict()
zoi_users_counter = OrderedDict()
per_users_counter = OrderedDict()
rep_users_counter = OrderedDict()
contacts_per_slot_per_user= OrderedDict()

copyfile('input-'+ file_name + '.json', str(uid)+'/input-'+ file_name + '.json') # Copy the corresponding input file into the folder
################## Loop per simulation
for s in range(0,num_sim):
    # seed = int(seed)
    # np.random.seed(seed_list[0])
    print("SIMULATION--> ", s)
    print("content size ", content_size)
    print("Max memory ", max_memory)

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
        # print("Number of users:", num_users)
    else:
        num_users=density_users
        # print("Number of users:", num_users)

    # print("Content size: ", content_size)

    # This creates N objects of ZOI class
    if num_zois_distribution == "poisson":
        num_zois = np.random.poisson(density_zois)
        # print("Number of zois:", num_zois)
    else:
        num_zois=density_zois
        # print("Number of zois:", num_zois)


    # CREATION OF SCENARIO With num_zois number of zois
    scenario = Scenario(radius_of_interest, radius_of_replication, radius_of_persistence, max_area,speed_distribution,pause_distribution,min_pause,max_pause, 
    min_speed,max_speed,delta,radius_of_tx,channel_rate,num_users,min_flight_length, max_flight_length,flight_length_distribution,hand_shake,num_zois)
    
    # CREATION OF ONE CONTENT PER ZOI and initializing counters of nodes with and without content per ZOI
    for z in scenario.zois_list:
        for m in range(0,num_contents):
            msg = Message(uuid.uuid4(),content_size,z)
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
                np.random.shuffle(z.content_list)
                user.messages_list.extend(z.content_list[:num_contents_node])
                zoi_users_counter[z] += 1
                zoi_counter[z] += 1
                for m in z.content_list:
                    m.counter += 1
            
            if user.zones[z] == "replication":
                np.random.shuffle(z.content_list)
                user.messages_list.extend(z.content_list[:num_contents_node])
                rep_users_counter[z] += 1
                rep_counter[z] += 1
                for m in z.content_list:
                    m.counter += 1
            
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
    attempts = []
    a_list = []
    a_per_zoi = OrderedDict()
    availability_per_zoi = OrderedDict()
    a_per_content = OrderedDict()

    # print("zoi_users_counter ",zoi_users_counter.values(),zoi_counter.values())
    # print("rep_users_counter ",rep_users_counter.values(),rep_counter.values())
    # print("per_users_counter ",per_users_counter.values(),per_counter.values())
    # Computing availability per ZOI and per CONTENT
    for z in scenario.zois_list:
        if (zoi_users_counter[z]+rep_users_counter[z]) == 0:
            av = 0
            for m in z.content_list:
                a_per_content[str(m.id)] = []
                a_per_content[str(m.id)].append(0)
        else:
            av = (zoi_counter[z] + rep_counter[z])/(zoi_users_counter[z]+rep_users_counter[z])
            for m in z.content_list:
                a_per_content[str(m.id)] = []
                a_per_content[str(m.id)].append(m.counter/(zoi_users_counter[z]+rep_users_counter[z]))

        a_per_zoi[z] = av
        availability_per_zoi[z] = []

    a = np.average(a_per_zoi.values())

    # print("per zoi availability: ", a_per_zoi.values())
    # print("this availability: " , a)

    availabilities_list_per_slot = []
    nodes_in_zoi = []
    c = 0
    
    ################## Loop per slot into a simulation
    while c < num_slots and a > 0:
        print("SLOT NUMBER: ", c)
        for z in scenario.zois_list:
            zoi_counter[z] = 0
            per_counter[z] = 0
            rep_counter[z]= 0
            zoi_users_counter[z] = 0
            per_users_counter[z] = 0
            rep_users_counter[z] = 0
            # Restart the counter for content availability
            for m in z.content_list:
                m.counter = 0

        bar.update(c+1)
        slots.append(c)
        c += 1

        # shuffle users lists
        np.random.shuffle(scenario.usr_list)

        # Run mobility for every slot           
        # Nobody should be BUSY at the beggining of a slot (busy means that the node has had a connection already in the current slot, so it cannot have another one)
        # Move every pedestrians once
        for j in range(0,num_users):
            scenario.usr_list[j].busy = False
            scenario.usr_list[j].randomDirection()

        # Run contacts for every slot after mobility.
        for k in range(0,num_users):
            # run users contact
            scenario.usr_list[k].hand_shake = hand_shake/delta
            scenario.usr_list[k].contacts_per_slot[c] = []
            scenario.usr_list[k].userContact(c)
        
        attempts.append(scenario.attempts)

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

                # Increment the content counter after moving and exchanging
                for m in scenario.usr_list[j].messages_list:
                    if m.zoi == z:
                        m.counter += 1
                
                # we are not counting the nodes that are out of every zoi

        ################################## Dump data per slot in a file ############################################
        
        zoi.append(zoi_counter[z])
        rep.append(rep_counter[z])
        per.append(per_counter[z])
        zoi_users.append(zoi_users_counter[z])
        rep_users.append(rep_users_counter[z])
        per_users.append(per_users_counter[z])

        # print("zoi_users_counter ",zoi_users_counter.values(),zoi_counter.values())
        # print("rep_users_counter ",rep_users_counter.values(),rep_counter.values())
        # print("per_users_counter ",per_users_counter.values(),per_counter.values())

        # we add the current slot availability to the list
        number_users_zoi = 0
        for z in scenario.zois_list:
            number_users_zoi = zoi_users_counter[z]+rep_users_counter[z]
            if (zoi_users_counter[z] + rep_users_counter[z]) == 0:
                av = 0
                for m in z.content_list:
                    a_per_content[str(m.id)].append(0)

            else:
                av = (zoi_counter[z] + rep_counter[z])/(zoi_users_counter[z]+rep_users_counter[z])
                for m in z.content_list:
                    a_per_content[str(m.id)].append(m.counter/(zoi_users_counter[z]+rep_users_counter[z]))

            a_per_zoi[z] = av
            availability_per_zoi[z].append(av)

        a = np.average(a_per_zoi.values())
        availabilities_list_per_slot.append(a)
        nodes_in_zoi.append(number_users_zoi)

        # print("per zoi availability: ", a_per_zoi.values())
        # print("this availability: " , a)

    # Add the availabilities in this simulation to the final list of availabilities
    avb_per_sim_per_slot.append(availabilities_list_per_slot)

    # At the end of every simulation we need to close connections and add it to the list of connection durations
    for k in range(0,num_users):
        if scenario.usr_list[k].ongoing_conn == True:
            if scenario.usr_list[k].connection_duration not in scenario.connection_duration_list.keys():
                scenario.connection_duration_list[scenario.usr_list[k].connection_duration] = 1
            else:
                scenario.connection_duration_list[scenario.usr_list[k].connection_duration] +=1

            scenario.usr_list[k].ongoing_conn = False
            scenario.usr_list[k].prev_peer.ongoing_conn = False
            # print("CONNEC DURATION out--> ", scenario.usr_list[k].connection_duration)
     
    for u in scenario.usr_list:
        contacts_per_slot_per_user[u.id] = u.contacts_per_slot

    ###################### Functions to dump data per simulation #########################
    dump = Dump(scenario,uid,s)
    dump.userLastPosition()
    dump.statisticsList(slots, zoi_users, zoi, rep_users, rep, per_users, per,attempts)
    dump.connectionDurationAndMore(contacts_per_slot_per_user)
    dump.availabilityPerZoi(availability_per_zoi.values())
    dump.availabilityPerSimulation(np.average(availabilities_list_per_slot))
    dump.listOfAveragesPerSlot(availabilities_list_per_slot)
    dump.con0exchange()
    dump.availabilityPerContent(a_per_content)
    dump.nodesZoiPerSlot(nodes_in_zoi)
    ########################## End of printing in simulation ##############################
    sys.stdout = orig_stdout
    f.close()
    bar.finish()
    t1 = time.time()
    print ("Total time running: %s minutes \n" % str((t1-t0)/60))