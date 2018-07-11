import numpy as np

class Message:
    'Common base class for all messages'
    

    def __init__(self, id, max_message_size):
        print ("Creating new message...")
        self.id = id
        self.size = np.random.randint(1,max_message_size) 
        self.displayMessage()


    def displayMessage(self):
        print("ID : ", self.id,  ", Size: ", self.size)