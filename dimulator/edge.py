from dimulator.message import Message

class AbstractEdge:
    def __init__(self, u, v, weight=1):
        self.__u = u
        self.__v = v
        self.__weight = weight
        self.width = 1
        self.color = 'k'
        self.style = 'solid'
        self.alpha = None
        self.label = None

    def __str__(self):
        return f'({self.node_u().identifier()}, {self.node_v().identifier()})'

    def node_u(self):
        return self.__u

    def node_v(self):
        return self.__v

    def weight(self):
        return self.__weight

    def opposite(self, node):
        if node==self.__u:
            return self.__v
        elif node==self.__v:
            return self.__u
        else:
            error_edge = f'edge ({self.__u.identifier()}, {self.__v.identifier()})'
            error_message = f'the node {node} is not connected'
            raise ValueError(f'{error_edge}: {error_message}')

class DirectedEdge(AbstractEdge):       # TODO everything
    def __init__(self, from_node, to_node, weight=1, connect=True):
        super().__init__(from_node, to_node, weight)
        if connect:
            self.connect()

    def from_node(self):
        return self.node_u()

    def to_node(self):
        return self.node_v()

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
        # TODO
        pass

    def frame_update(self, t):
        # TODO
        pass


class UndirectedEdge(AbstractEdge):
    def __init__(self, u, v, weight=1, connect=True):
        super().__init__(u, v, weight)
        self.sending_uv = {}        # {message: living}
        self.sending_vu = {}
        if connect:
            self.connect()

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
            self.sending_uv[message] = 1
        elif from_node == self.node_v():
            self.sending_vu[message] = 1
        else:
            error_edge = f'edge ({self.node_u().identifier()}, {self.node_v().identifier()})'
            error_message = f'the message "{message}" is injected by unknown node {from_node}'
            raise ValueError(f'{error_edge}: {error_message}')


    def frame_update(self, t):
        for msg, living in list(self.sending_uv.items()):
            self.sending_uv[msg] = living + 1
            if living > self.weight():
                self.node_v().receive_message(msg)
                self.sending_uv.pop(msg)
        for msg, living in list(self.sending_vu.items()):
            self.sending_vu[msg] = living + 1
            if living >= self.weight():
                self.node_u().receive_message(msg)
                self.sending_vu.pop(msg)
