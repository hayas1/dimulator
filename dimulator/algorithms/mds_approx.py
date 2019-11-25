from dimulator.node import UndirectedNode
from dimulator.graph import UndirectedGraph
from dimulator.daemon import FairDaemon
from dimulator.layout import antigravity_node_layout, degree_base_edge_layout

import os

import numpy as np
import matplotlib.pyplot as plt

class MDSAprproxNode(UndirectedNode):
    def __init__(self, id=None, k=10, max_degree=None):
        super().__init__(id=id)
        self.max_degree = 1
        self.mds_x = 0
        self.dy_degree = 1
        self.k = k
        self.gray_or_white = 'white'

    def inirialize(self, max_degree):
        self.max_degree = max_degree
        self.dy_degree = self.degree()

    def synch_update(self, round, message_tuples):
        self.lp_mds_approx(round, message_tuples)
        pass

    def lp_mds_approx(self, round, message_tuples):
        l = round // self.k
        h = round % self.k
        self.bloadcast(self.gray_or_white)
        self.dy_degree = sum(m=='white' for e, m in message_tuples)     #TODO 送ったメッセージに対応する受信
        if self.dy_degree >= (self.max_degree+1)**(l/self.k):
            self.mds_x = max(self.mds_x, 1/(self.max_degree+1)**(h/self.k))
        self.bloadcast(self.mds_x)
        if sum(m for e, m in message_tuples):
            self.gray_or_white = 'gray'

