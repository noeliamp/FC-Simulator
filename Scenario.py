from Zoi import Zoi
import numpy as np
from collections import OrderedDict


class Scenario:
    'Common base class for all scenarios'

    def __init__(self, radius_of_interest, radius_of_replication, radius_of_persistence, max_area, speed_distribution,pause_distribution,min_pause,max_pause,
    min_speed,max_speed,delta,radius_of_tx,channel_rate,num_users,min_flight_length, max_flight_length,flight_length_distribution, hand_shake,num_zois):
        print ("Creating new scenario...")
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
        self.attempts = 0
        self.count_0_exchange_conn = 0
        self.count_non_useful = 0
        self.count_useful = 0
        self.connection_duration_list = OrderedDict()
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

