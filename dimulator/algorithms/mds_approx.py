from dimulator.node import UndirectedNode
from dimulator.graph import UndirectedGraph
from dimulator.daemon import FairDaemon
from dimulator.layout import antigravity_node_layout, degree_base_edge_layout

import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import colorConverter

class MDSAprproxNode(UndirectedNode):
    def __init__(self, id=None, k=5, max_degree=None):
        super().__init__(id=id)
        self.max_degree = 1
        self.mds_approx_x = 0
        self.dy_degree = 1
        self.k = k
        self.gray_or_white = 'white'
        self.end_approx = False
        self.mds_x = 0

    def initialize(self, max_degree):
        self.max_degree = max_degree
        self.dy_degree = self.degree()

    def synch_update(self, round, message_tuples):
        if round <= self.k**2:
            l = self.k - round // self.k
            h = self.k - round % self.k
            self.lp_mds_approx(round, message_tuples, l, h)
            self.color = self.gray_or_white     # for animation
            self.transparency = self.mds_approx_x       # for animation
        elif self.k**2 < round < self.k**2 + 3:
            self.end_approx = True
        else:
            self.mds_rounding(round-(self.k**2+3), message_tuples)

    def lp_mds_approx(self, round, message_tuples, l, h):
        self.dy_degree = sum(m[0]=='white' for e, m in message_tuples)
        sum_of_neighbors_x = sum(m[1] for e, m in message_tuples)
        if self.dy_degree >= (self.max_degree+1)**(l/self.k):
            self.mds_approx_x = max(self.mds_approx_x, 1/(self.max_degree+1)**(h/self.k))
        if self.mds_approx_x + sum_of_neighbors_x >= 1:
            self.gray_or_white = 'gray'
        self.bloadcast(self.make_message((self.gray_or_white, self.mds_approx_x), size=10 + 90*self.mds_approx_x, color=self.gray_or_white))

    def mds_rounding(self, round, message_tuples):
        if round == 0:
            self.bloadcast(self.make_message(self.degree(), size=50))
        elif round == 1:
            neighbors_max_degree = max(m for e, m in message_tuples)
            self.bloadcast(self.make_message(neighbors_max_degree, size=100))
        elif round == 2:
            two_neighbors_max_degree = max(m for e, m in message_tuples)
            p = min(1, self.mds_approx_x * np.log(two_neighbors_max_degree+1))
            self.mds_x = 1 if np.random.rand() < p else 0
            self.bloadcast(self.mds_x)
            self.transparency = 1       # for animation
            self.color = 'c' if self.mds_x else 'w'     # for animation
        elif round == 3:
            if all(m!=1 for e, m in message_tuples):
                self.mds_x = 1
            self.transparency = 1       # for animation
            self.color = 'c' if self.mds_x else 'w'     # for animation

def animate_minimum_dominating_set_approx(n=15, frames=None):
    # make node
    nodes = list(MDSAprproxNode(id=i, k=5) for i in range(n))

    # make graph and set node
    graph = UndirectedGraph(nodes=nodes)

    # compute node position
    pos = antigravity_node_layout(nodes)

    # make and set edge
    for u, v, dist in degree_base_edge_layout(pos):
        graph.connect_undirected_edge(u, v, weight=min(20, 300/(1+np.exp(-(3*dist-5)))))

    # set max degree as initial knowledge
    for node in nodes:
        node.max_degree = graph.max_degree()

    # initialize give node n
    for node in nodes:
        node.initialize(graph.max_degree())

    # make daemon and set graph
    daemon = FairDaemon(graph, conflict=False)

    # start animation
    return daemon.animation(pos, weight=False, label=False, interval=100, frames=frames or n*10)

def save_msd_approx_as_gif(n=15, frames=None, dir='./out', file='msd_approx.gif'):
    os.makedirs(dir, exist_ok=True)
    ani = animate_minimum_dominating_set_approx(n=n, frames=frames)
    ani.save(f'{dir}/{file}', fps=10)

def animate_mds_rounding(n=15, frames=None):
    k = 5
    # make node
    nodes = list(MDSAprproxNode(id=i, k=k) for i in range(n))

    # make graph and set node
    graph = UndirectedGraph(nodes=nodes)

    # compute node position
    pos = antigravity_node_layout(nodes)

    # make and set edge
    for u, v, dist in degree_base_edge_layout(pos):
        graph.connect_undirected_edge(u, v, weight=min(20, 300/(1+np.exp(-(3*dist-5)))))

    # set max degree as initial knowledge
    for node in nodes:
        node.max_degree = graph.max_degree()

    # initialize give node n
    for node in nodes:
        node.initialize(graph.max_degree())

    # make daemon and set graph
    daemon = FairDaemon(graph, conflict=False)

    # run lpmds approx
    daemon.main_loop(until=lambda: all(node.end_approx for node in nodes))

    # start animation
    return daemon.animation(pos, weight=False, label=False, interval=100, frames=frames or n*10)

def save_msd_rounding_as_gif(n=15, frames=None, dir='./out', file='msd_rounding.gif'):
    os.makedirs(dir, exist_ok=True)
    ani = animate_mds_rounding(n=n, frames=frames)
    ani.save(f'{dir}/{file}', fps=10)