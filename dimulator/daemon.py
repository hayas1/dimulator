from dimulator.message import make_message

import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.animation as anm

class AbstractDaemon:
    def __init__(self, graph, conflict=True):
        self.__graph = graph
        self.conflict = conflict

    def graph(self):
        return self.__graph

    def choose(self):
        return [], []

    def main_loop(self, timeout=10**3, until=lambda: False):
        t = 0
        while((not until()) and (t < timeout)):
            self.each_loop(t)
            t += 1
        if until():
            print('the algorithm terminated successfully')
        if t >= timeout:
            print(f'time out: the algorithm do not terminated {timeout} frame')

    def each_loop(self, t):
        nodes, edges = self.choose()
        for node in nodes:
            node.frame_update(t)
        for edge in edges:
            edge.frame_update(t, conflict=self.conflict)

    def animation(self, pos, weight=False, label=False, interval=100, frames=20):
        g = self.graph().to_networkx_graph(weight=weight)
        fig, ax = plt.subplots()
        artists = ax.plot([], [])
        def init():
            return [ax]
        return anm.FuncAnimation(fig, self.each_draw_network, init_func=init, fargs=(artists, g, pos, label),
                                 interval=interval, frames=frames, blit=False)

    def each_draw_network(self, t, artists, g, pos, label=True):
        plt.cla()
        plt.title(f'time: {t}')
        self.graph().draw_networkx(g, pos, label=label)

        edges = self.graph().edges()
        for edge in edges:
            u_pos, v_pos = np.array(pos[edge.node_u()]), np.array(pos[edge.node_v()])
            for msg_wrapper in edge.sending():
                msgpos = edge.message_pos(msg_wrapper, u_pos, v_pos)
                message = msg_wrapper.message()
                msg_dict = message.dict_for_scatter() if hasattr(message, 'dict_for_scatter') else make_message(message).dict_for_scatter()
                plt.scatter(*msgpos, **msg_dict)

        self.each_loop(t)
        return artists



class CentralDaemon(AbstractDaemon):
    pass #TODO


class FairDaemon(AbstractDaemon):
    def __init__(self, graph, conflict=True):
        super().__init__(graph, conflict=conflict)
        self.update_interval = self.graph().max_weight()

    def choose(self):
        return self.graph().nodes(), self.graph().edges()

    def each_loop(self, t):
        nodes, edges = self.choose()
        for node in nodes:
            node.frame_update(t, t%self.update_interval==0)
        for edge in edges:
            edge.frame_update(t, conflict=self.conflict)

    # TODO refactoring to better override
    def each_draw_network(self, t, artists, g, pos, label=True):
        plt.cla()
        plt.title(f'time: {t}, round: {t // self.update_interval}')
        self.graph().draw_networkx(g, pos, label=label)

        edges = self.graph().edges()
        for edge in edges:
            u_pos, v_pos = np.array(pos[edge.node_u()]), np.array(pos[edge.node_v()])
            for msg_wrapper in edge.sending():
                msgpos = edge.message_pos(msg_wrapper, u_pos, v_pos)
                message = msg_wrapper.message()
                msg_dict = message.dict_for_scatter()
                plt.scatter(*msgpos, **msg_dict)

        self.each_loop(t)
        return artists


class UnfairDaemon(AbstractDaemon):
    pass #TODO
