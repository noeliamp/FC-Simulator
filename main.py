from User import User
from Dump import Dump
from Message import Message
from Scenario import Scenario
import numpy as np
import json
from collections import OrderedDict
import sys
from random import shuffle
import uuid

orig_stdout = sys.stdout
f = open('out.txt', 'w')
sys.stdout = f

file = open('dump.txt', 'w')

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

    

usrList = []                                            # list of users
statusList = ['available', 'infected']

# This creates N objects of User class
if num_users_distribution == "poisson":
    num_users = np.random.poisson(density)
    print("Number of users:", num_users)
else:
    num_users=density

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

file.write('Number of users: '+ str(scenario.num_users) + '\n')
file.write('SLOT '+ ' ZOI '+' REP '+ ' PER '+ ' OUT ' '\n')

for i in range(0,num_slots):
    slots.append(i)
    # Run mobility for every slot
    print ('\n Lets run mobility slot: %d' % i)
    # Nobody is BUSY at the beggining of a slot
    for l in range(0,num_users):
        scenario.usrList[l].buys = False
    # Move every pedestrian once
    for j in range(0,num_users):
        scenario.usrList[j].randomDirection()


    # Run contacts for every slot after mobility, at the beggining of every slot every user is available --> busy = Flase
    print ('\n Lets run contacts slot: %d' % i)
    for k in range(0,num_users):
        scenario.usrList[k].busy = False

    # suffle users lists
    shuffle(scenario.usrList)
    for k in range(0,num_users):
        scenario.usrList[k].userContact()



    ################################## Dump data per slot in a file ############################################
    zoi_counter= 0
    per_counter = 0
    rep_counter= 0
    out_counter = 0
    for k in range(0,num_users):
        if scenario.usrList[k].zone == "interest" and len(scenario.usrList[k].messages_list) == 1:
            zoi_counter = zoi_counter + 1
        
    for k in range(0,num_users):
        if scenario.usrList[k].zone == "replication" and len(scenario.usrList[k].messages_list) == 1:
            rep_counter = rep_counter + 1
        
    for k in range(0,num_users):
        if scenario.usrList[k].zone == "persistence" and len(scenario.usrList[k].messages_list) == 1:
            per_counter = per_counter + 1
        
    for k in range(0,num_users):
        if scenario.usrList[k].zone == "outer" and len(scenario.usrList[k].messages_list) == 1:
            out_counter = out_counter + 1
        
    zoi.append(zoi_counter)
    rep.append(rep_counter)
    per.append(per_counter)
    out.append(out_counter)

    # for i in range(0,num_users): 
        # file.write('%i %i %i %i' % (zoi[i], rep[i], per[i], out[i]))
    # file.write(str(zoi_counter) + ' - ' + str(rep_counter) + ' - ' + str(per_counter) + ' - ' + str(out_counter) + '\n')
print(len(slots),len(zoi),len(rep),len(per),len(out))
np.savetxt('dump.txt', np.column_stack((slots, zoi, rep, per, out)), fmt="%i %i %i %i %i")
###################### SELECT A FUNCTION TO DUMP DATA ###########################
# dump = Dump(scenario)
# dump.userLastPosition()
# dump.infoPerZone()


########################## End of printing ######################################
sys.stdout = orig_stdout
f.close()

file.close()