import numpy as np

class Message:
    'Common base class for all messages'

    def __init__(self, id, max_message_size, scenario,slot):
        # print ("Creating new message...")
        self.id = id
        self.size = max_message_size
        self.counter = [0] * scenario.num_zois
        self.creation_slot = slot
        # self.displayMessage()


    def displayMessage(self):
        print("ID : ", self.id,  ", Size: ", self.size, ", Counter: ", self.counter)