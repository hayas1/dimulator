import random
from dimulator import node

class Daemon:
    def __init__(self, nodes):
        self.nodes = nodes

    def choose(self):
        return self.nodes



class Central_daemon(Daemon):
    def __init__(self, nodes):
        self.nodes = nodes

    def choose(self):
        return random.choice(self.nodes)





class Fair_daemon(Daemon):
    pass #TODO


class Unfair_daemon(Daemon):
    pass #TODO
