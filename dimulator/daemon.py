import random
from dimulator import node

class AbstractDaemon:
    def __init__(self, graph):
        self.__graph = graph

    def graph(self):
        return self.__graph

    def choose(self):
        return [], []

    def each_loop(self, t):
        nodes, edges = self.choose()
        for node in nodes:
            node.frame_update(t)
        for edge in edges:
            edge.frame_update(t)

    def main_loop(self, timeout=10**3, until=lambda: False):
        t = 0
        while((not until()) and (t < timeout)):
            self.each_loop(t)
            t += 1
        if until():
            print('the algorithm terminated successfully')
        if t >= timeout:
            print(f'time out: the algorithm do not terminated {timeout} frame')

    def each_draw_network(self, t, )

class CentralDaemon(AbstractDaemon):
    pass #TODO


class FairDaemon(AbstractDaemon):
    def __init__(self, graph):
        super().__init__(graph)
        self.update_interval = self.graph().max_weight()

    def choose(self):
        return self.graph().nodes(), self.graph().edges()

    def each_loop(self, t):
        nodes, edges = self.choose()
        for node in nodes:
            node.frame_update(t, t%self.update_interval==0)
        for edge in edges:
            edge.frame_update(t)


class UnfairDaemon(AbstractDaemon):
    pass #TODO
