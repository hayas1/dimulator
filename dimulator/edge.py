from collections import deque

import numpy as np

class MessageWrapper:
    def __init__(self, message, from_node, to_node):
        self.__msg = message
        self.__from = from_node
        self.__to = to_node
        self.__living = 0

    def message(self):
        return self.__msg

    def from_node(self):
        return self.__from

    def to_node(self):
        return self.__to

    def living(self):
        return self.__living

    def frame_update(self, t):
        self.__living += 1

    def progress(self, edge_weight):
        return self.__living / edge_weight

class AbstractEdge:
    def __init__(self, u, v, weight=10):
        self.__u = u
        self.__v = v
        self.__weight = int(weight)
        self.width = 1
        self.color = 'k'
        self.style = 'solid'
        self.transparency = None        #cannot reflect, due to networkx's API
        self.label = None

    def __str__(self):
        return f'({self.node_u().identifier()}, {self.node_v().identifier()})'

    def node_u(self):
        return self.__u

    def node_v(self):
        return self.__v

    @property
    def weight(self):
        return self.__weight
    @weight.setter
    def weight(self, w):
        self.__weight = int(w)

    def attr_dict(self):
        return {'width': self.width, 'color': self.color, 'style': self.style, 'alpha': self.transparency, 'label': self.label}

    def to_networkx_edge(self, weight=False):     #if node eject this edge, graph include this edge
        return (self.node_u(), self.node_v(), {'w': self.weight}) if weight else (self.node_u(), self.node_v(), self.attr_dict())

    def same_path(self, u, v):
        return (self.node_u() == u) and (self.node_v() == v)

    def opposite(self, node):
        if node==self.__u:
            return self.__v
        elif node==self.__v:
            return self.__u
        else:
            error_edge = f'edge ({self.__u.identifier()}, {self.__v.identifier()})'
            error_message = f'the node {node} is not connected'
            raise ValueError(f'{error_edge}: {error_message}')

class DirectedEdge(AbstractEdge):
    def __init__(self, from_node, to_node, weight=10, connect=True):
        super().__init__(from_node, to_node, weight)
        self.__sending = deque([None]*self.weight)
        if connect:
            self.connect()

    def __str__(self):
        return f'directed ({self.from_node().identifier()}, {self.to_node().identifier()}, (weight:{self.weight}))'

    def from_node(self):
        return self.node_u()

    def to_node(self):
        return self.node_v()

    def sending(self):
        return list(filter(lambda m: m != None, self.__sending))

    def sending_state(self):
        return list(self.__sending)

    def connect(self):
        if not self.from_node().connectability(self):
            self.from_node().add_outgoing(self)
        if not self.to_node().connectability(self):
            self.to_node().add_incoming(self)

    def eject(self):
        if self.from_node().connectability(self):
            self.from_node().eject_outgoing(self)
        if self.to_node().connectability(self):
            self.to_node().eject_incoming(self)

    def inject(self, message):
        self.__sending[0] = MessageWrapper(message, self.from_node(), self.to_node())

    def post(self, message_wrapper, undirected=None):
        if self.to_node().connectability(self) and undirected==None:
            self.to_node().receive_message(self, message_wrapper.message())
        else:
            self.to_node().receive_message(undirected, message_wrapper.message())
        # # self.__sending.remove(message_wrapper)
        # self.__sending[-1] = None

    def lost_message_pos(self, pos):
        self.__sending[pos] = None

    def lost_message(self, message_wrapper):
        self.lost_message_pos(self.__sending.index(message_wrapper))

    def frame_update(self, t, undirected=None):
        for msg_wrapper in filter(lambda m: m != None, self.__sending):
            msg_wrapper.frame_update(t)
            # if msg_wrapper.living() >= self.weight:
            #     self.post(msg_wrapper, undirected=undirected)
        if self.__sending[-1] != None:
            self.post(self.__sending[-1], undirected=undirected)
            self.__sending[-1] = None
        self.__sending.rotate()

    def message_pos(self, message, from_pos, to_pos):
        f, t = np.array(from_pos), np.array(to_pos)
        return f + (t - f) * message.living() / self.weight



class UndirectedEdge(AbstractEdge):
    def __init__(self, u, v, weight=10, connect=True):
        super().__init__(u, v, weight)
        self.u_to_v = DirectedEdge(u, v, weight=weight, connect=False)
        self.v_to_u = DirectedEdge(v, u, weight=weight, connect=False)
        if connect:
            self.connect()

    def __str__(self):
        return f'undirected ({self.node_u().identifier()}, {self.node_v().identifier()}, (weight:{self.weight}))'

    @property
    def weight(self):
        return super().weight
    @weight.setter
    def weight(self, w):
        super().weight = int(w)
        self.u_to_v.weight = int(w)
        self.v_to_u.weight = int(w)

    def sending(self):
        messages = self.u_to_v.sending()
        messages.extend(self.v_to_u.sending())
        return messages     # flatten

    def same_path(self, u, v):
        return ((self.node_u() == u) and (self.node_v() == v)) or  ((self.node_u() == v) and (self.node_v() == u))

    def connect(self):
        u, v = self.node_u(), self.node_v()
        if not u.connectability(self):
            u.add_edge(self)
        if not v.connectability(self):
            v.add_edge(self)

    def eject(self):
        u, v = self.node_u(), self.node_v()
        if u.connectability(self):
            u.eject_edge(self)
        if v.connectability(self):
            v.eject_edge(self)

    def inject(self, from_node, message):
        if from_node == self.node_u():
            self.u_to_v.inject(message)
        elif from_node == self.node_v():
            self.v_to_u.inject(message)
        else:
            error_edge = f'undirected edge ({self.node_u().identifier()}, {self.node_v().identifier()})'
            error_message = f'the message "{message}" is injected by unknown node {from_node}'
            raise ValueError(f'{error_edge}: {error_message}')

    def post(self, message_wrapper):
        if message_wrapper in self.u_to_v.sending():
            return self.u_to_v.post(message_wrapper, undirected=self)
        elif message_wrapper in self.v_to_u.sending():
            return self.v_to_u.post(message_wrapper, undirected=self)
        else:
            error_edge = f'undirected edge ({self.node_u().identifier()}, {self.node_v().identifier()})'
            error_message = f'the message "{message_wrapper.message()}" is not sending by this edge'
            raise KeyError(f'{error_edge}: {error_message}')

    def frame_update(self, t, conflict=True):
        for msg_uv, msg_vu in zip(self.u_to_v.sending_state(), reversed(self.v_to_u.sending_state())):
            if conflict and msg_uv!=None and msg_vu!=None:
                self.u_to_v.lost_message(msg_uv)
                self.v_to_u.lost_message(msg_vu)
        self.u_to_v.frame_update(t, undirected=self)
        # TODO refactoring: very bad copy and paste implement
        for msg_uv, msg_vu in zip(self.u_to_v.sending_state(), reversed(self.v_to_u.sending_state())):
            if conflict and msg_uv!=None and msg_vu!=None:
                self.u_to_v.lost_message(msg_uv)
                self.v_to_u.lost_message(msg_vu)
        self.v_to_u.frame_update(t, undirected=self)


    def message_pos(self, message_wrapper, u_pos, v_pos):
        if message_wrapper in self.u_to_v.sending():
            return self.u_to_v.message_pos(message_wrapper, u_pos, v_pos)
        elif message_wrapper in self.v_to_u.sending():
            return self.v_to_u.message_pos(message_wrapper, v_pos, u_pos)
        else:
            error_edge = f'undirected edge ({self.node_u().identifier()}, {self.node_v().identifier()})'
            error_message = f'the message "{message_wrapper.message()}" is not sending by this edge'
            raise KeyError(f'{error_edge}: {error_message}')


