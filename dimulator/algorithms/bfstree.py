from dimulator.node import UndirectedNode
from dimulator.graph import UndirectedGraph
from dimulator.daemon import FairDaemon
from dimulator.layout import antigravity_node_layout, degree_base_edge_layout

import os

import numpy as np


class BFSTreeNode(UndirectedNode):
    def __init__(self, id=None, root=False):
        super().__init__(id=id)
        self.parent = None
        self.root = root
        self.msg = None
        self.bloadcasted = False    # for animation

    def synch_update(self, round, message_tuples):
        if round==0 and self.root==True:
            self.color = 'r'    # for animation
            self.msg = (self.identifier(), 'pulse')
        if self.msg != None:
            if self.bloadcasted:    # for animation
                self.msg = self.make_message(self.msg, size=30, alpha=0.5)  # for animation
        self.bloadcast(self.msg)
        if self.msg:
            self.bloadcasted = True     # for animation
        _, r = tuple(zip(*message_tuples)) if message_tuples else (None, ())
        if r and self.parent==None:
            vj_id, pulse = r[0]
            self.parent = vj_id
            self.edge(vj_id).color = 'r'  # for animation
            self.msg = (self.identifier(), pulse)

def animate_breadth_first_tree(n=15, frames=None):
    # make node
    nodes = list(BFSTreeNode(id=i) for i in range(n-1))
    nodes.append(BFSTreeNode(id=n-1, root=True))

    # make graph and set node
    graph = UndirectedGraph(nodes=nodes)

    # compute node position
    pos = antigravity_node_layout(nodes)

    # make and set edge
    for u, v, dist in degree_base_edge_layout(pos):
        graph.connect_undirected_edge(u, v, weight=min(20, 300/(1+np.exp(-(3*dist-5)))))

    # make daemon and set graph
    daemon = FairDaemon(graph)

    # start animation
    return daemon.animation(pos, weight=False, label=False, interval=100, frames=frames or n*10)

def save_bfs_as_gif(n=15, frames=None, dir='./out', file='bfstree.gif'):
    os.makedirs(dir, exist_ok=True)
    ani = animate_breadth_first_tree(n=n, frames=frames)
    ani.save(f'{dir}/{file}', fps=10)