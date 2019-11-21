class Message:
    def __init__(self, message):
        self.__living = 0
        self.__msg = message
        
    def frame_update(self, t):
        self.__living += 1
        
    def message(self):
        return self.__msg