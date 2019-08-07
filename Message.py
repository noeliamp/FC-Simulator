import numpy as np

class Message:
    'Common base class for all messages'

    def __init__(self, id, max_message_size, scenario,slot):
        # print ("Creating new message...")
        self.id = id
        self.scenario = scenario
        self.size = max_message_size
        self.counter = [0] * scenario.num_zois
        self.creation_slot = slot
        self.ttl = 0
        # self.displayMessage()


    def displayMessage(self):
        print("ID : ", self.id,  ", Size: ", self.size, ", Counter: ", self.counter)


    def die(self):
        # remove the content from the zois first
        for z in self.scenario.zois_list:
            for m in z.content_list:
                if m.id == self.id:
                    z.content_list.remove(m)
        
        # remove the content from the users
        for u in self.scenario.usr_list:
            for m in u.messages_list:
                if m.id == self.id:
                    u.messages_list.remove(m)
                    u.used_memory -= m.size
                    # if m in u.exchange_list:
