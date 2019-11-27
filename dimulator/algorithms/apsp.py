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

# in pseudocode, after node get token, it send token at each round
class APSPNode(UndirectedNode):
    CMAP = plt.get_cmap('gist_rainbow')

    def __init__(self, id=None, bfs_root=True):
        super().__init__(id=id)
        self.bfs_root = bfs_root
        self.parents = {}
        self.bloadcasted = []
        self.bloadcasting = {}
        self.msg_switch_buff = deque([] for _ in range(2))

    def make_aveilable_color(self, n):      # for animation
        self.apsp_color = list(APSPNode.CMAP(i/n) for i in range(n))

    def initialize(self, root=False):
        self.root = root
        self.token = root
        self.dfs_parent = None
        self.unvisited = self.neighbors()
        self.start_bfs_round = np.inf
        if root:
            self.color = self.apsp_color[self.identifier()]

    def synch_update(self, round, message_tuples):
        self.msg_switch_buff[0] = message_tuples
        self.msg_switch_buff.rotate()
        if round % 2 == 0:
            self.token_circulation(round, self.msg_switch_buff[0])
        elif round % 2 == 1:
            self.bfs_for_apsp(round-self.start_bfs_round, self.msg_switch_buff[0])

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
            self.color = self.apsp_color[self.identifier()]    # for animation
            self.bloadcasting[self.identifier()] = (self.identifier(), 'pulse', self.identifier())
            self.parents[self.identifier()] = self.identifier()
        if self.bloadcasting:
            # if self.identifier() == 0: print(f'id0 bloadcasting {self.bloadcasting}')
            root, msg = (self.identifier(), self.bloadcasting.pop(self.identifier())) if round==0 else self.bloadcasting.popitem()
            self.bloadcast(self.make_message(msg, color=self.apsp_color[root]), without=[self.parents.get(root, None)])
            # if self.identifier() == 0: print(f'id0 bloadcasted {msg}, when root {root}')
            self.bloadcasted.append(root)   # only one times broadcast for one root
        if message_tuples:
            for vj_id, pulse, root in [m for e, m in message_tuples if len(m)==3]:
                if self.parents.get(root, True):     # no parent, return True
                    self.parents[root] = vj_id
                    self.bloadcasting[root] = (self.identifier(), pulse, root)
                    # if self.identifier == 0: print(f'id0: vj_id: {vj_id}, pulse: {pulse}, root: {root}, and broadcasting {(self.identifier(), pulse, root)}')


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

    ### this information use only for animation ###
    for node in nodes:
        node.make_aveilable_color(graph.n())

    # initialize node
    for node in nodes:
        if node.identifier() == n-1:
            node.initialize(root=True)
        else:
            node.initialize(root=False)

    # make daemon and set graph
    daemon = FairDaemon(graph, conflict=False)

    # start animation
    return daemon.animation(pos, weight=False, label=False, interval=100, frames=frames or n*10), nodes

def save_apsp_as_gif(n=15, frames=None, dir='./out', file='apsp.gif'):
    os.makedirs(dir, exist_ok=True)
    ani, _ = animate_all_pair_shortest_path(n=n, frames=frames)
    ani.save(f'{dir}/{file}', fps=10)