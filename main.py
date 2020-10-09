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
os.mkdir("results/" + uid)
print(uid)

# Copy the corresponding input file into the folder
copyfile('input-'+ file_name + '.json', "results/"+ str(uid)+'/input-'+ file_name + '.json') 

# Start timer for simulation time
t0 = time.time()

# Read the input file
with open('input-'+ file_name + '.json') as f:
    data = json.load(f)

density_users = data["num_users"]
density_zois = data["num_zois"]
radius_of_tx = data["radius_of_tx"]                     # area to look for neigbors (dependent on contact range)
max_area = data["max_area_squared"]                     # outer zone - max area size
radius_of_replication = data["radius_of_replication"]   # second zone - replication
delta = data["delta"]                                   # time per slot
channel_rate = data["channel_rate"]
max_message_size = data["max_message_size"]
min_message_size = data["min_message_size"]
content_size = np.random.uniform(max_message_size, min_message_size)
max_memory = data["num_contents_node"] * content_size                        # max memory allowed per user device
num_contents_node = data["num_contents_node"]
content_generation_time = data["content_generation_time"]
content_generation_users = data["content_generation_users"]
traces_folder = data["traces_folder"]
num_slots = data["num_slots"]                           # number of repetitions in one simulation
max_time_elapsed = data["max_time_elapsed"]
ttl = num_slots
algorithm = data["algorithm"]
if algorithm == "PIS":
    gamma = data["gamma"]
else:
    gamma = -100000
store = data["store"]
days = str(int((num_slots/3600)/24))
statis = data["statis"]
alp = data["alp"]

# Do we want to set a seed?
seed_list = [15482669,15482681,15482683,15482711,15482729,15482941,15482947,15482977,15482993,15483023,15483029,15483067,15483077,15483079,15483089,15483101,15483103,15482743,15482771,15482773,15482783,15482807,15482809,15482827,15482851,15482861,15482893,15482911,15482917,15482923]
seed = int(traces_file)
np.random.seed(seed_list[1])

print("Content size ", content_size)
print("Max memory ", max_memory)
print("Number of contents ", content_generation_users)

def dumping():
    for u in scenario.usr_list:
        rzs_per_slot_per_user[u.id] = u.rz_visits_info
        
        contact_mean[0] = u.prev_contact_mean[0]
        contact_mean[1] = u.prev_contact_mean[1]
        contact_mean[2] = u.prev_contact_mean[-1]

        contact_len_mean[0] = u.prev_contact_len_mean[0]
        contact_len_mean[1] = u.prev_contact_len_mean[1]
        contact_len_mean[2] = u.prev_contact_len_mean[-1]

        probabilities[u.id] = u.prob

        if u.id not in contacts_per_node.keys():
            contacts_per_node[u.id] = OrderedDict()
        contacts_per_node[u.id] = u.dicc_peers


    ###################### Functions to dump data per simulation #########################
    dump = Dump(scenario,uid)
    dump.userLastPosition()
    dump.connectionDurationAndMore(contents_per_slot_per_user,rzs_per_slot_per_user,contact_mean,contact_len_mean,a_per_content_only_value,contacts_per_node)
    dump.availabilityPerContent(a_per_content)
    dump.replicasPerContent(replicas)
    dump.nodesZoiPerSlot(nodes_in_zoi)
    dump.probabilities(probabilities)
    dump.nodesInRz()
    

# DATA STRUCTURES 
contacts_per_node = OrderedDict()
contents_per_slot_per_user= OrderedDict()
rzs_per_slot_per_user = OrderedDict()
contact_len_mean = OrderedDict()
contact_mean = OrderedDict()
nodes_in_zoi = OrderedDict()
probabilities = OrderedDict()
c = 1 # Slot number
a_per_content = OrderedDict()
replicas = OrderedDict()
a_per_content_only_value = OrderedDict()
num_users=density_users
num_zois=density_zois


# CREATION OF SCENARIO With num_zois number of zois
scenario = Scenario(radius_of_replication, max_area,delta,radius_of_tx,channel_rate,num_users,num_zois, traces_folder,
num_slots,algorithm,max_memory,max_time_elapsed,gamma,statis,alp)


# From here on, start printing out to an external file called 'out'
orig_stdout = sys.stdout
f = open('results/'+str(uid)+'/out.txt', 'w')
sys.stdout = f    

################## Parse traces in case we are using them
traces_file = days
if "Paderborn" in traces_folder:
    scenario.parsePaderbornTraces(traces_folder,traces_file)

if traces_folder == "Rome":
    scenario.parseRomaTraces(traces_folder,traces_file,days)

if traces_folder == "SanFrancisco":
    scenario.parseSanFranciscoTraces(traces_folder)

if traces_folder == "Luxembourg":
    scenario.parseLuxembourgTraces(traces_folder,traces_file)

# Start users counter in every zoi to 0
for z in scenario.zois_list:
    nodes_in_zoi[z.id] = OrderedDict()
    nodes_in_zoi[z.id][0] = 0

# CREATION OF USERS with traces

if "Paderborn" not in traces_folder:
    scenario.addRemoveNodes(0)


# creating availability data structures per CONTENT per ZOI
for z in scenario.zois_list:
    for m in z.content_list:
        a_per_content[str(m.id)] = OrderedDict()
        a_per_content[str(m.id)][0] = []
        a_per_content[str(m.id)][1] = []
        replicas[str(m.id)] = OrderedDict()
        replicas[str(m.id)][0] = []
        replicas[str(m.id)][1] = []
        a_per_content_only_value[str(m.id)] = OrderedDict()
        a_per_content_only_value[str(m.id)][0] = 0
        a_per_content_only_value[str(m.id)][1] = 0





# Simulation STARTS!!!
# progress bar
bar = progressbar.ProgressBar(maxval=num_slots, \
    widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
bar.start()
################## ################## Loop per slot into a simulation ################## ##################
nextHop = 1030
if "Paderborn" not in traces_folder:
    scenario.cutTracesDict(0,nextHop)
while c < num_slots:
    print("SLOT-->",c)
    bar.update(c)

    if c % 1000 == 0 and "Paderborn" not in traces_folder:
        scenario.cutTracesDict(c,c+nextHop)

    if "Paderborn" not in traces_folder:
        scenario.addRemoveNodes(c)


    # shuffle users lists
    np.random.shuffle(scenario.usr_list)

    for z in scenario.zois_list:
        # Restart the counter for nodes in each zoi
        nodes_in_zoi[z.id][c] = 0
        # Restart the counter for each content availability in each zoi
        for m in z.content_list:
            m.counter[0] = 0
            m.counter[1] = 0
            m.counter[2] = 0

    for m in scenario.zois_list[0].content_list:       
        # if message ttl is over, kill the content, otherwise increment counter for ttl
        if m.ttl == ttl:
            m.die()
        else:
            m.ttl += 1
    
    # Creating new contents if required at the specific time slot
    if content_generation_time != "none":
        if c % content_generation_time == 0 or c == 1:
            userCounter=0
            np.random.shuffle(scenario.usr_list)
            for u in scenario.usr_list:
                if u.current_zoi != -1:
                    msg = Message(uuid.uuid4(),content_size,scenario,c)
                    u.messages_list.append(msg)  
                    userCounter+=1
                    scenario.zois_list[u.current_zoi].content_list.append(msg)
                    if userCounter == content_generation_users:
                        break


    # Run mobility for every slot           
    # Nobody should be BUSY at the beginning of a slot (busy means that the node has had a connection already in the current slot, so it cannot have another one)
    # Move every pedestrian once
    for j in scenario.usr_list:
        j.busy = False
        j.readTraces(c)

        if j.current_zoi == -1 and scenario.algorithm != 'PIS':
            for z in scenario.zois_list:
                j.checkDB(z,c)
                # j.checkHistory(c)

        j.getContacts(c)


    if scenario.algorithm == "PIS":
        for j in scenario.usr_list:
            j.socialFactorsUpdating(c)
            j.similaritiesCalculation(c)
            
    # Run contacts for every slot after mobility.
    for k in scenario.usr_list:
        # run users contact
        if scenario.algorithm == 'out' and scenario.num_slots != scenario.max_time_elapsed:
            # k.computeStatistics(c)
            k.userContactOutIn(c)
        if scenario.algorithm == 'in':
            # k.computeStatistics(c)
            k.userContact(c)
        if scenario.algorithm == 'PIS' or (scenario.algorithm == 'out' and scenario.num_slots == scenario.max_time_elapsed):
            k.userContactOutIn(c)
           
        # After moving the nodes and exchanging content, check to which zone they belong to increase the right counter
        if k.current_zoi != -1:
            nodes_in_zoi[k.current_zoi][c] += 1
            # Increment the content counter after moving and exchanging
            for m in k.messages_list:
                m.counter[k.current_zoi] += 1

        # only to count if there are messages out of the zois  
        if k.current_zoi == -1:
            # Increment the content counter after moving and exchanging
            for m in k.messages_list:
                m.counter[2] += 1

    # scenario.addRemoveNodes(c)
    ################################## Availability ############################################
    # we add the current slot availability to the list
    
    for z in scenario.zois_list:
        for m in z.content_list:
            if str(m.id) not in a_per_content:
                if c % 20 == 0:
                    a_per_content[str(m.id)] = OrderedDict()
                    a_per_content[str(m.id)][0] = [0] * int(c/20)
                    a_per_content[str(m.id)][1] = [0] * int(c/20)
                if c == 0:
                    a_per_content[str(m.id)] = OrderedDict()
                    a_per_content[str(m.id)][0]= []
                    a_per_content[str(m.id)][1] = []
                a_per_content_only_value[str(m.id)] = OrderedDict()
                a_per_content_only_value[str(m.id)][0] = 0
                a_per_content_only_value[str(m.id)][1] = 0
            # first add availability for ZOI 0
            nodes = nodes_in_zoi[0][c]
            if c % 20 == 0:
                if nodes != 0:
                    a_per_content[str(m.id)][0].append(m.counter[0]/nodes)
                else:
                    if m.counter[2] > 0 or m.counter[1]>0:
                        a_per_content[str(m.id)][0].append(0.000000000001)
                    else:
                        a_per_content[str(m.id)][0].append(0)
            if a_per_content_only_value[str(m.id)][0] != 0:
                if nodes != 0:
                    a_per_content_only_value[str(m.id)][0] = ((m.availability_counter_0*a_per_content_only_value[str(m.id)][0])+(m.counter[0]/nodes))/(m.availability_counter_0+1)
                else:
                    a_per_content_only_value[str(m.id)][0] = ((m.availability_counter_0*a_per_content_only_value[str(m.id)][0])+(0))/(m.availability_counter_0+1)
                m.availability_counter_0 = m.availability_counter_0 + 1
            if a_per_content_only_value[str(m.id)][0] == 0:
                if nodes != 0:
                    a_per_content_only_value[str(m.id)][0] = m.counter[0]/nodes
                else:
                    a_per_content_only_value[str(m.id)][0] = 0
                m.availability_counter_0 = m.availability_counter_0 + 1
            # Second add availability for ZOI 1
            if c % 20 == 0:
                nodes = nodes_in_zoi[1][c]
                if nodes !=0:
                    a_per_content[str(m.id)][1].append(m.counter[1]/nodes)
                else:
                    if m.counter[2] > 0 or m.counter[0]>0:
                        a_per_content[str(m.id)][1].append(0.000000000001)
                    else:
                        a_per_content[str(m.id)][1].append(0)
            if a_per_content_only_value[str(m.id)][1] != 0:
                if nodes !=0:
                    a_per_content_only_value[str(m.id)][1] = ((m.availability_counter_1*a_per_content_only_value[str(m.id)][1])+(m.counter[1]/nodes))/(m.availability_counter_1+1)
                else:
                    a_per_content_only_value[str(m.id)][1] = ((m.availability_counter_1*a_per_content_only_value[str(m.id)][1])+(0))/(m.availability_counter_1+1)
                m.availability_counter_1 = m.availability_counter_1 + 1
            if a_per_content_only_value[str(m.id)][1] == 0:
                if nodes != 0:
                    a_per_content_only_value[str(m.id)][1] = m.counter[1]/nodes
                else:
                    a_per_content_only_value[str(m.id)][1] = 0
                m.availability_counter_1 = m.availability_counter_1 + 1
        
            ### replicas
            if str(m.id) not in replicas:
                if c % 20 == 0 and c!= 0:
                    replicas[str(m.id)] = OrderedDict()
                    replicas[str(m.id)][0] = [0] * int((c/20))
                    replicas[str(m.id)][1] = [0] * int((c/20))
                if c == 0:
                    replicas[str(m.id)] = OrderedDict()
                    replicas[str(m.id)][0]= []
                    replicas[str(m.id)][1] = []
            if c % 20 == 0:
                replicas[str(m.id)][0].append(m.counter[0])
                replicas[str(m.id)][1].append(m.counter[1])
        
    
    if c % 20 == 0:
        contents_per_slot_per_user[c] = OrderedDict()
        for u in scenario.usr_list:
            if u.id not in contents_per_slot_per_user[c]:
                contents_per_slot_per_user[c][u.id]= []
            contents_per_slot_per_user[c][u.id].append(len(u.messages_list))

    if c != 0 and c % 1000 == 0:
        dumping()

    c += 1
    ################################## ############## ############################################

# At the end of every simulation we need to close connections and add them to the list of connection durations
for k in scenario.usr_list:
    if k.ongoing_conn == True:
        if k.connection_duration not in scenario.connection_duration_list.keys():
            scenario.connection_duration_list[k.connection_duration] = 1
        else:
            scenario.connection_duration_list[k.connection_duration] +=1

        k.ongoing_conn = False
        k.prev_peer.ongoing_conn = False

         # Add the location of the connection
        previous_zoi = k.myFuture[num_slots-1]
        if previous_zoi not in k.scenario.connection_location_list.keys():
            k.scenario.connection_location_list[previous_zoi] = 1
        else:
            k.scenario.connection_location_list[previous_zoi] +=1


dumping()
########################## End of printing in simulation ##############################
sys.stdout = orig_stdout
f.close()
bar.finish()
t1 = time.time()
print ("Total time running: %s minutes \n" % str((t1-t0)/60))
print(c)