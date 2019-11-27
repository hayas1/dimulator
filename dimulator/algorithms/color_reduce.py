from dimulator.node import UndirectedNode
from dimulator.graph import UndirectedGraph
from dimulator.daemon import FairDaemon
from dimulator.layout import antigravity_node_layout, degree_base_edge_layout

import os

import numpy as np
import matplotlib.pyplot as plt

class ColorReduceNode(UndirectedNode):
    CMAP = plt.get_cmap('gist_rainbow')

    def __init__(self, id=None, color=None):
        super().__init__(id=id)
        self.c = color if color!=None else id
        self.nc = []

    def make_aveilable_color(self, n, max_degree):      # for animation
        self.initial_color = list(ColorReduceNode.CMAP(i/n) for i in range(n))
        self.aveilable_color = list(ColorReduceNode.CMAP(i/max_degree) for i in range(max_degree))

    def synch_update(self, round, message_tuples):
        if round == 0:
            self.nc.extend(m for e, m in message_tuples)
            self.color = self.initial_color[self.c-1]      # for animation
            self.bloadcast(self.make_message(self.c, color=self.initial_color[self.c-1]))
        else:
            self.nc.extend(m for e, m in message_tuples)
            if self.c == round:
                self.c = self.min_color()
                self.color = self.aveilable_color[self.c-1]      # for animation
                self.bloadcast(self.make_message(self.c, color=self.aveilable_color[self.c-1]))


    def min_color(self):    # return minimum color not in self.nc (larger than or equal 1):
        i = 1
        for c in sorted(self.nc):   # sort make O(n log n)
            if i < c:
                return i
            else:
                i = c + 1
        else:
            return i


def animate_color_reduce(n=15, frames=None):
    # make node
    nodes = list(ColorReduceNode(id=i+1, color=i+1) for i in range(n))

    # make graph and set node
    graph = UndirectedGraph(nodes=nodes)

    # compute node position
    pos = antigravity_node_layout(nodes)

    # make and set edge
    for u, v, dist in degree_base_edge_layout(pos):
        graph.connect_undirected_edge(u, v, weight=min(20, 300/(1+np.exp(-(3*dist-5)))))

    ### this information use only for animation ###
    for node in nodes:
        node.make_aveilable_color(graph.n(), graph.max_degree())

    # make daemon and set graph
    daemon = FairDaemon(graph, conflict=False)

    # start animation
    return daemon.animation(pos, weight=False, label=False, interval=100, frames=frames or n*10)

def save_color_reduce_as_gif(n=15, frames=None, dir='./out', file='color_reduce.gif'):
    os.makedirs(dir, exist_ok=True)
    ani = animate_color_reduce(n=n, frames=frames)
    ani.save(f'{dir}/{file}', fps=10)