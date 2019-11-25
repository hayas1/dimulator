from dimulator.node import UndirectedNode
from dimulator.graph import UndirectedGraph
from dimulator.daemon import FairDaemon
from dimulator.layout import antigravity_node_layout, degree_base_edge_layout
# from dimulator.algorithms.color_reduce import ColorReduceNode

import os

import numpy as np
import matplotlib.pyplot as plt

class ColoringNode(UndirectedNode):
    CMAP = plt.get_cmap('gist_rainbow')

    def __init__(self, id=None, max_degree=None):
        super().__init__(id=id)
        self.c = None
        self.induced_nc = {}
        self.recursive_arguments = []
        self.recursive_return = None
        self.max_degree = max_degree or self.degree()
        self.coloring_round = 0
        self.coloring_x = None

    def make_aveilable_color(self, n, max_degree):      # for animation
        # self.initial_color = list(ColoringNode.CMAP(i/n) for i in range(n))
        self.aveilable_color = list(ColoringNode.CMAP(i/max_degree) for i in range(2 *(max_degree + 1)))

    def synch_update(self, round, message_tuples):
        if round == self.coloring_round:
            self.x = self.coloring(round, message_tuples)
        else:
            self.color_reduce_induced(round%self.coloring_round, message_tuples, self.x)

    def coloring(self, round, message_tuples):
        if round == 0:
            binary = format(self.identifier(), 'b')
            for i in range(1, len(binary)+1):   # in pseucode, use recursive call, but it is difficult so use stuck
                self.recursive_arguments.append(binary[-i:])
        x = self.recursive_arguments.pop() if self.recursive_arguments else format(self.identifier(), 'b').zfill(round+1)
        if format(self.identifier(), 'b') == x:
            self.c = 1
            self.recursive_return = self.c
        elif format(self.identifier(), 'b').startswith(x):
            b = format(self.identifier(), 'b')[:len(x)+1]
            self.c = self.recursive_return
            if b.endswith('1'):
                self.c += self.max_degree + 1
            self.color = self.aveilable_color[self.c-1]      # for animation
        self.coloring_round = round + 2 * (self.max_degree+1)
        # print('next coloring', self.coloring_round)
        return x

    def color_reduce_induced(self, round, message_tuples, x):
        if self.identifier() == 7:
            print(f'id7, round{round}, induced {x}, neighbor{list(m[0] for e, m in message_tuples if m[1]==x)}')
        if round == 0:
            self.induced_nc.get(x, []).extend(m[0] for e, m in message_tuples if m[1]==x)
            self.color = self.aveilable_color[self.c-1]      # for animation
            self.bloadcast(self.make_message((self.c, x), color=self.aveilable_color[self.c-1]))
        else:
            self.induced_nc.get(x, []).extend(m[0] for e, m in message_tuples if m[1]==x)
            if self.c == round:
                self.c = self.induced_min_color(x)
                self.color = self.aveilable_color[self.c-1]      # for animation
                self.bloadcast(self.make_message((self.c, x), color=self.aveilable_color[self.c-1]))


    def induced_min_color(self, x):    # return minimum color not in self.nc (larger than or equal 1):
        i = 1
        for c in sorted(self.induced_nc.get(x, [])):   # sort make O(n log n)
            if i < c:
                return i
            else:
                i = c + 1
        else:
            return i




def animate_coloring(n=15, frames=None):
    # make node
    nodes = list(ColoringNode(id=i) for i in range(n))

    # make graph and set node
    graph = UndirectedGraph(nodes=nodes)

    # compute node position
    pos = antigravity_node_layout(nodes)

    # make and set edge
    for u, v, dist in degree_base_edge_layout(pos):
        # graph.connect_undirected_edge(u, v, weight=min(20, 300/(1+np.exp(-(3*dist-5)))))
        graph.connect_undirected_edge(u, v, weight=6)

    # set max degree as initial knowledge
    for node in nodes:
        node.max_degree = graph.max_degree()

    ### this information use only for animation ###
    for node in nodes:
        node.make_aveilable_color(graph.n(), graph.max_degree())

    # make daemon and set graph
    daemon = FairDaemon(graph)

    # start animation
    return daemon.animation(pos, weight=False, label=False, interval=100, frames=frames or n*10)

def save_coloring_as_gif(n=15, frames=None, dir='./out', file='coloring.gif'):
    os.makedirs(dir, exist_ok=True)
    ani = animate_coloring(n=n, frames=frames)
    ani.save(f'{dir}/{file}', fps=15)