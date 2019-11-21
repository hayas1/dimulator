from dimulator.message import Message

class AbstractNode:
    def __init__(self, id=None, size=300, color='#1f78b4', bcolor='k', bwidth=1, alpha=None, label=None):
        self.__id = id
        self.size = size
        self.color = color
        self.label = label
        self.border_color = bcolor
        self.border_width = bwidth
        self.transparency = alpha

    def identifier(self):
        return self.__id


class DirectedNode(AbstractNode):       # TODO processing message and so on...
    def __init__(self, id=None, size=300, color='#1f78b4', bcolor='k', bwidth=1, alpha=None, label=None):
        super().__init__(id=id, size=size, color=color, bcolor=bcolor, bwidth=bwidth, alpha=alpha, label=label)
        self.outgoings = []
        self.incomings = []

    def __str__(self):
        return str(self.identifier())

    def add_outgoing(self, directed_edge, recursive=False):
        self.outgoings.extend(directed_edge) if recursive else self.outgoings.append(directed_edge)

    def add_incoming(self, directed_edge, recursive=False):
        self.outgoings.extend(directed_edge) if recursive else self.incomings.append(directed_edge)

    def eject_outgoing(self, directed_edge, recursive=False):
        if recursive:
            for edge in directed_edge:
                self.outgoings.remove(edge)
        else:
            self.outgoings.remove(directed_edge)

    def eject_incoming(self, directed_edge, recursive=False):
        if recursive:
            for edge in directed_edge:
                self.incomings.remove(edge)
        else:
            self.incomings.remove(directed_edge)

    def connectability(self, edge):
        return (edge in self.outgoings) or (edge in self.incomings)

    def sendable_nodes(self):
        return [edge.opposite(self) for edge in self.outgoings]

    def receivable_nodes(self):
        return [edge.opposite(self) for edge in self.incomings]

    def frame_update(self, t):
        # TODO processing received message
        pass

    # TODO
    # def synch_update(self, t, msg):
    #     pass

class UndirectedNode(AbstractNode):
    def __init__(self, id=None, size=300, color='#1f78b4', bcolor='k', bwidth=1, alpha=None, label=None):
        super().__init__(id=id, size=size, color=color, bcolor=bcolor, bwidth=bwidth, alpha=alpha, label=label)
        self.__edges = []
        self.__nei_to_edge = {}     # when compute neighbors, this dictionary update
        self.__received = []

    def __str__(self):
        neighbors = f'{", ".join(str(neighbor.identifier()) for neighbor in self.neighbors())}'
        return f'{{id: {self.identifier()}, neighbors: [{neighbors}]}}'

    def edges(self):
        return list(self.__edges)

    def add_edge(self, undirected_edge, recursive=False):
        self.__edges.extend(undirected_edge) if recursive else self.__edges.append(undirected_edge)

    def eject_edge(self, undirected_edge, recursive=False):
        if recursive:
            for edge in undirected_edge:
                self.__edges.remove(edge)
        else:
            self.__edges.remove(undirected_edge)

    def connectability(self, edge):
        return edge in self.__edges

    def neighbors(self):
        nodes = []
        for edge in self.__edges:
            neighbor = edge.opposite(self)
            nodes.append(neighbor)
            self.__nei_to_edge[neighbor] = edge
        return nodes

    def send_message(self, neighbor, message, duality=False):
        if (duality == False) and (neighbor in self.__nei_to_edge):
            self.__nei_to_edge[neighbor].inject(self, message)
        else:
            for edge in self.__edges:
                if edge.opposite(self) == neighbor:
                    edge.inject(self, message)

    def bloadcast(self, message, recursive=False):
        if recursive:
            for neighbor, msg in zip(self.neighbors(), message):
                self.send_message(neighbor, msg)
        else:
            for neighbor in self.neighbors():
                self.send_message(neighbor, message)

    def flooding(self, message):
        for edge in self.__edges:
            edge.inject(self, message)

    def receive_message(self, message):
        self.__received.append(message)

    def frame_update(self, t):
        print(t, self.__received)

    def synch_update(self, t, msg):
        pass