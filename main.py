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


# Read from command line: input file and number of simulations
file_name = str(sys.argv[1])
traces_file = str(sys.argv[2])
print('input-'+ file_name + '.json')
print('traces file number: ' + traces_file)

# Generate a unique uid for the simulation and create a new folder with that uid to store the dump files
uid = base64.urlsafe_b64encode(hashlib.md5(os.urandom(128)).digest())[:8]
uid =  str(file_name) + "-"+ str(uid) 
os.mkdir(uid)
print(uid)

# Copy the corresponding input file into the folder
copyfile('input-'+ file_name + '.json', str(uid)+'/input-'+ file_name + '.json') 

# Start timer for simulation time
t0 = time.time()

# Read the input file
with open('input-'+ file_name + '.json') as f:
    data = json.load(f)

num_sim = data["num_sim"]                               # number of simulations
density_users = data["num_users"]
density_zois = data["num_zois"]
num_users_distribution = data["num_users_distribution"] # number of users distribution
num_zois_distribution = data["num_zois_distribution"]   # number of zois distribution
radius_of_tx = data["radius_of_tx"]                     # area to look for neigbors (dependent on contact range)
max_area = data["max_area_squared"]                     # outer zone - max area size
radius_of_interest = data["radius_of_interest"]         # inner zone - interest
radius_of_replication = data["radius_of_replication"]   # second zone - replication
min_speed = data["min_speed"]
max_speed = data["max_speed"]
min_pause = data["min_pause"]
max_pause = data["max_pause"]
speed_distribution = data["speed_distribution"]
pause_distribution = data["pause_distribution"]
delta = data["delta"]                                   # time per slot
channel_rate = data["channel_rate"]
max_message_size = data["max_message_size"]
min_message_size = data["min_message_size"]
content_size = np.random.uniform(max_message_size, min_message_size)
max_memory = data["num_contents_node"] * content_size                        # max memory allowed per user device
min_flight_length = data["min_flight_length"]
max_flight_length = data["max_flight_length"]
flight_length_distribution = data["flight_length_distribution"]
hand_shake = data["hand_shake"]
num_contents = data["num_contents"]
num_contents_node = data["num_contents_node"]
content_generation_time = data["content_generation_time"]
content_generation_users = data["content_generation_users"]
traces_folder = data["traces_folder"]
num_slots = data["num_slots"]                           # number of repetitions in one simulation
max_time_elapsed = data["max_time_elapsed"]
ttl = data["msg_ttl"]

# Do we want to set a seed?
# seed_list = [15482669,15482681,15482683,15482711,15482729,15482941,15482947,15482977,15482993,15483023,15483029,15483067,15483077,15483079,15483089,15483101,15483103,15482743,15482771,15482773,15482783,15482807,15482809,15482827,15482851,15482861,15482893,15482911,15482917,15482923]
# seed = int(seed)
# np.random.seed(seed_list[0])

print("Content size ", content_size)
print("Max memory ", max_memory)

# Frpm here on, start printing out to an external file called out
orig_stdout = sys.stdout
# f = open(os.devnull, 'w')
f = open(str(uid)+'/out.txt', 'w')
sys.stdout = f      


# Simulation STARTS!!!
# progress bar
bar = progressbar.ProgressBar(maxval=num_slots, \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
bar.start()

# DATA STRUCTURES 
contacts_per_slot_per_user= OrderedDict()
usr_list = []        # list of users in the entire scenario
nodes_in_zoi = OrderedDict()
c = 0 # Slot number
attempts = []
a_per_content = OrderedDict()

# Define number of users in case we want poisson distribution, otherwise fixed number
if num_users_distribution == "poisson":
    num_users = np.random.poisson(density_users)
else:
    num_users=density_users


# Define number of ZOIs in case we want poisson distribution, otherwise fixed number
if num_zois_distribution == "poisson":
    num_zois = np.random.poisson(density_zois)
else:
    num_zois=density_zois


# CREATION OF SCENARIO With num_zois number of zois
scenario = Scenario(radius_of_interest, radius_of_replication, max_area,speed_distribution,pause_distribution,min_pause,max_pause, 
min_speed,max_speed,delta,radius_of_tx,channel_rate,num_users,min_flight_length, max_flight_length,flight_length_distribution,hand_shake,num_zois, traces_folder,num_slots)

################## Parse traces in case we are using them
if traces_folder != "none":
    scenario.parseTraces(traces_folder,traces_file)

# CREATION OF CONTENTS
for m in range(0,num_contents):
    msg = Message(uuid.uuid4(),content_size,scenario,0)
    # To measure availability in all zois we need to include each msg in every zoi
    for o in scenario.zois_list:
        o.content_list.append(msg)

# Start users counter in every zoi to 0
for z in scenario.zois_list:
    nodes_in_zoi[z.id] = 0

# CREATION OF USERS
for i in range(0,num_users):
    # Look for the initial position of each node only if we are using traces
    if traces_folder != "none":
        # print("Initial Position: ", scenario.tracesDic[str(i)].items()[0][1][0],scenario.tracesDic[str(i)].items()[0][1][1])
        x = scenario.tracesDic[str(i)].items()[0][1][0]
        y = scenario.tracesDic[str(i)].items()[0][1][1] 
        user = User(i,x,y, scenario,max_memory,max_time_elapsed)
        user.predict(num_slots)
        
    # If we are not using traces, the initial position is random
    else:
        user = User(i,np.random.uniform(-max_area, max_area),np.random.uniform(-max_area, max_area), scenario,max_memory,max_time_elapsed)

    # add the content to each user according to the ZOIs that they belong to
    for z in user.zones.keys():
        # to compute the first availability (if node is not out it will have the message for sure)
        np.random.shuffle(z.content_list)
        if num_contents_node < num_contents:
            user.messages_list.extend(z.content_list[:num_contents_node])
        else:
            user.messages_list.extend(z.content_list[:num_contents])

        # Increase the counter for nodes in each zoi 
        nodes_in_zoi[z.id] += 1
        # and the number of nodes having each content in that zoi
        for m in user.messages_list:
            m.counter[z.id] += 1

    # now we set the amount of memory used by the node according to the messages that were included in its list.
    for m in user.messages_list:
        user.used_memory += m.size                     

    usr_list.append(user)


# add the list of users to every scenario
scenario.usr_list = usr_list

# Computing availability per CONTENT per ZOI
for z in scenario.zois_list:
    if nodes_in_zoi[z.id] == 0:
        for m in z.content_list:
            a_per_content[str(m.id)] = OrderedDict()
            a_per_content[str(m.id)][z.id] = []
            a_per_content[str(m.id)][z.id].append(0)
    else:
        for m in z.content_list:
            a_per_content[str(m.id)] = OrderedDict()
            a_per_content[str(m.id)][z.id] = []
            a_per_content[str(m.id)][z.id].append(m.counter[z.id]/nodes_in_zoi[z.id])


    print("this availability at zoi : " , z.id , a_per_content[str(m.id)][z.id],m.counter[z.id], nodes_in_zoi[z.id] )

################## ################## Loop per slot into a simulation ################## ##################
while c < num_slots:
    # print("SLOT NUMBER: ", c)
    c += 1
    bar.update(c)

    # shuffle users lists
    np.random.shuffle(scenario.usr_list)

    for z in scenario.zois_list:
        # Restart the counter for nodes in each zoi
        nodes_in_zoi[z.id] = 0
        # Restart the counter for each content availability in each zoi
        for m in z.content_list:
            m.counter[z.id] = 0
            # if message ttl is over, kill the content, otherwise increment counter for ttl
            if m.ttl == ttl:
                print("im dying")
                m.die()
            else:
                m.ttl += 1
    
    # Creating new contents if required at the specific time slot
    if content_generation_time != "none":
        if c % content_generation_time == 0:
            userCounter=0
            for u in scenario.usr_list:
                if len(u.zones) > 0:
                    # print("User id ", u.id)
                    msg = Message(uuid.uuid4(),content_size,scenario,c)
                    print("Creating contents at slot: ", c)
                    # print("User msg list ", len(u.messages_list))
                    u.messages_list.append(msg)  
                    u.used_memory += msg.size           
                    # print("User msg list ", len(u.messages_list))
                    userCounter+=1
                    for o in scenario.zois_list:
                        o.content_list.append(msg)
                    if userCounter == content_generation_users:
                        break


    # Run mobility for every slot           
    # Nobody should be BUSY at the beginning of a slot (busy means that the node has had a connection already in the current slot, so it cannot have another one)
    # Move every pedestrian once
    for j in range(0,num_users):
        scenario.usr_list[j].busy = False
        if traces_folder == "none":
            scenario.usr_list[j].randomDirection()
        else:
            scenario.usr_list[j].readTraces(c)
            
        # Check the new point zone of the user
        scenario.usr_list[j].calculateZones()


    # Run contacts for every slot after mobility.
    for k in range(0,num_users):
        # run users contact
        scenario.usr_list[k].hand_shake = hand_shake/delta
        scenario.usr_list[k].contacts_per_slot[c] = []
        scenario.usr_list[k].userContactOut(c)
    
    # count attempts of connections per slot
    attempts.append(scenario.attempts)

    # After moving the nodes and exchanging content, check to which zone they belong to increase the right counter
    for j in range(0,num_users):
        for z in scenario.usr_list[j].zones.keys():
            nodes_in_zoi[z.id] += 1
            # Increment the content counter after moving and exchanging
            for m in scenario.usr_list[j].messages_list:
                m.counter[z.id] += 1
            
    ################################## Availability ############################################
    # we add the current slot availability to the list
    for z in scenario.zois_list:
        if nodes_in_zoi[z.id] == 0:
            for m in z.content_list:
                if str(m.id) not in a_per_content:
                    a_per_content[str(m.id)] = OrderedDict()
                if z.id not in a_per_content[str(m.id)]:
                    a_per_content[str(m.id)][z.id] = []
                a_per_content[str(m.id)][z.id].append(0)

        else:
            for m in z.content_list:
                if str(m.id) not in a_per_content:
                    a_per_content[str(m.id)] = OrderedDict()
                if z.id not in a_per_content[str(m.id)]:
                    a_per_content[str(m.id)][z.id] = []
                    # fill the availability list with 0 to match the slot in which the content was created
                    a_per_content[str(m.id)][z.id][:c] = [0] * c
                a_per_content[str(m.id)][z.id].append(m.counter[z.id]/nodes_in_zoi[z.id])
                print("availability: ", m.counter[z.id], nodes_in_zoi[z.id])

    ################################## ############## ############################################

# At the end of every simulation we need to close connections and add them to the list of connection durations
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
dump = Dump(scenario,uid)
dump.userLastPosition()
dump.connectionDurationAndMore(contacts_per_slot_per_user)
dump.con0exchange()
dump.availabilityPerContent(a_per_content)
dump.nodesZoiPerSlot(nodes_in_zoi)
dump.nodesPath()
########################## End of printing in simulation ##############################
sys.stdout = orig_stdout
f.close()
bar.finish()
t1 = time.time()
print ("Total time running: %s minutes \n" % str((t1-t0)/60))