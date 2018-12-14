import numpy as np

class Message:
    'Common base class for all messages'

    def __init__(self, id, max_message_size, zoi):
        # print ("Creating new message...")
        self.id = id
        self.size = max_message_size
        self.zoi = zoi
        self.counter = 0
        # self.displayMessage()


    def displayMessage(self):
        print("ID : ", self.id,  ", Size: ", self.size,  ", ZOI: ", self.zoi.id,  ", Counter: ", self.counter)