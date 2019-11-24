from dimulator.node import UndirectedNode
from dimulator.graph import UndirectedGraph
from dimulator.daemon import FairDaemon
from dimulator.layout import antigravity_node_layout, degree_base_edge_layout
# from dimulator.algorithms.bfstree import BFSTreeNode
from dimulator.message import AbstractMessage

import os
from collections import deque

import numpy as np
import matplotlib.pyplot as plt

class APSPNode(UndirectedNode):
    def __init__(self, id=1, bfs_root=True):
        super().__init__(id=id)
        self.bfs_root = bfs_root
        self.parent = {}
        self.bloadcasted = []
        self.bloadcasting = {}
        self.cmap = plt.get_cmap('tab10')
        self.odd_even_msg_controller = deque([] for _ in range(2))

    def initialize(self, root=False):
        self.root = root
        self.token = root
        self.dfs_parent = None
        self.unvisited = self.neighbors()
        self.start_bfs_round = np.inf
        if root:
            self.color = 'r'    # for animation

    def synch_update(self, round, message_tuples):
        self.odd_even_msg_controller[0] = message_tuples
        self.odd_even_msg_controller.rotate()
        if round % 2 == 0:
            self.token_circulation(round, self.odd_even_msg_controller[0])
        elif round % 2 == 1:
            self.bfs_for_apsp(round-self.start_bfs_round, self.odd_even_msg_controller[0])

    def token_circulation(self, round, message_tuples):
        if self.token == True:
            if self.unvisited:
                v = self.unvisited[0]
                self.unvisited.remove(v)    # in pseucode, randomize instead of remove, but it makes bad perfomance, so i remove token parent
            else:
                if self.root == True:
                    return
                v = self.dfs_parent
            self.send_message(v, self.make_message((self.identifier(), 'token'), size=150, shape='s', color='r'))    # for animation
            self.bloadcast(self.make_message((self.identifier(), 'visited'), size=50, alpha=0.5, color='c'), without=[v])      # for animation
        _, r = tuple(zip(*message_tuples)) if message_tuples else (None, ())
        if any(m[1]=='token' for m in r):
            vj_id, _ = next(filter(lambda em: em[1]=='token', r), None)
            self.token = True
            if vj_id in self.unvisited:
                self.unvisited.remove(vj_id)    # in pseucode, randomize instead of remove, but it makes bad perfomance, so i remove token parent
            if self.dfs_parent == None:
                self.dfs_parent = vj_id
                self.edge(vj_id).color = 'c'   # for animation
                self.start_bfs_round = round + 1 # start bfs-tree algorithm at round r+2
        else:
            for vj_id, _ in filter(lambda vm: vm[1]=='visited', r):
                if vj_id in self.unvisited:     # in pseudocode, remove without check, but no element cannot remove from list in python
                    self.unvisited.remove(vj_id)

    def bfs_for_apsp(self, round, message_tuples):
        if round==0 and self.bfs_root==True:
            self.color = self.cmap(self.identifier())    # for animation
            self.bloadcasting[self.identifier()] = (self.identifier(), 'pulse', self.identifier())
            # print(f'round {round}, id{self.identifier()} want to bloadcast {(self.identifier(), "pulse", self.identifier())}')
        if self.bloadcasting:
            # print(f'round {round}, id{self.identifier()}, bloadcasting {self.bloadcasting}')
            root, msg = self.identifier(), self.bloadcasting.pop(self.identifier()) if round==0 else self.bloadcasting.popitem()
            self.bloadcast(self.make_message(msg, color=self.cmap(root)))
            self.bloadcasted.append(root)   # only one times broadcast for one root
        _, r = tuple(zip(*message_tuples)) if message_tuples else (None, ())
        if r:
            for vj_id, pulse, root in filter(lambda vmr: vmr[1]=='pulse', r):
                if self.parent.get(root, True):     # no parent, return True
                    self.parent[root] = vj_id
                    self.bloadcasting[root] = (self.identifier(), pulse, root)
                    # self.edge(vj_id).color = 'r'  # for animation


def animate_all_pair_shortest_path(n=15, frames=None):
    # make node
    nodes = list(APSPNode(id=i) for i in range(n))

    # make graph and set node
    graph = UndirectedGraph(nodes=nodes)

    # compute node position
    pos = antigravity_node_layout(nodes)

    # make and set edge
    for u, v, dist in degree_base_edge_layout(pos):
        graph.connect_undirected_edge(u, v, weight=min(10, 300/(1+np.exp(-(3*dist-5)))))

    # initialize node
    for node in nodes:
        if node.identifier() == n-1:
            node.initialize(root=True)
        else:
            node.initialize(root=False)

    # make daemon and set graph
    daemon = FairDaemon(graph)

    # start animation
    return daemon.animation(pos, weight=False, label=False, interval=100, frames=frames or n*10)

def save_apsp_as_gif(n=15, frames=None, dir='./out', file='apsp.gif'):
    os.makedirs(dir, exist_ok=True)
    ani = animate_all_pair_shortest_path(n=n, frames=frames)
    ani.save(f'{dir}/{file}', fps=15)