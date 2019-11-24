from dimulator.message import make_message, AbstractMessage

class AbstractNode:
    SHAPE = 'o'

    def __init__(self, id=None, size=300, color='#1f78b4', bcolor='k', bwidth=1, alpha=1, label=None):
        self.__id = id
        self.size = size
        self.color = color
        self.border_color = bcolor
        self.border_width = bwidth
        self.transparency = alpha
        self.label = label

    def identifier(self):
        return self.__id

    def __str__(self):
        return f'{str(self.identifier())}'

    def make_message(self, message, size=100, shape='o', color='#ff9999', bcolor='k', bwidth=1, alpha=1, label=None):
        return make_message(message, size=size, shape=shape, color=color, bcolor=bcolor, bwidth=bwidth, alpha=alpha, label=label)

    def attr_dict(self):
        return {'size': self.size, 'color': self.color, 'label': self.label, 'bcolor': self.border_color,
                'bwidth': self.border_width, 'alpha': self.transparency}

    def to_networkx_node(self):
        return self, self.attr_dict()


class DirectedNode(AbstractNode):       # TODO processing message and so on...
    def __init__(self, id=None, size=300, color='#1f78b4', bcolor='k', bwidth=1, alpha=1, label=None):
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
    def __init__(self, id=None, size=300, color='#1f78b4', bcolor='k', bwidth=1, alpha=1, label=None):
        super().__init__(id=id, size=size, color=color, bcolor=bcolor, bwidth=bwidth, alpha=alpha, label=label)
        self.__edges = []
        self.__nei_to_edge = {}     # when compute neighbors, this dictionary update
        self.__received = []    # [(edge, message), ...]
        self.__round_counter = self.round_counter()

    # def __str__(self):
    #     neighbors = f'{", ".join(str(neighbor.identifier()) for neighbor in self.neighbors())}'
    #     return f'{{id: {self.identifier()}, neighbors: [{neighbors}]}}'


    def edges(self):
        return list(self.__edges)

    def recieved(self):
        return list(self.__received)

    def add_edge(self, undirected_edge, recursive=False):
        self.__edges.extend(undirected_edge) if recursive else self.__edges.append(undirected_edge)

    def eject_edge(self, undirected_edge, recursive=False):
        if recursive:
            for edge in undirected_edge:
                self.__edges.remove(edge)
        else:
            self.__edges.remove(undirected_edge)

    def __id_to_neighbor(self, id):
        return next(filter(lambda x: x.identifier()==id, self.neighbors(id=False)), None)

    def edge(self, neighbor, id=True):
        nei = self.__id_to_neighbor(neighbor) if id else neighbor
        return self.__nei_to_edge.get(nei, None)

    def connectability(self, edge):
        return edge in self.__edges

    def neighbors(self, id=True):        #TODO return not neighbor's object but neighbor's identifier
        nodes = []
        for edge in self.__edges:
            neighbor = edge.opposite(self)
            nodes.append(neighbor.identifier()) if id else nodes.append(neighbor)
            self.__nei_to_edge[neighbor] = edge
        return nodes

    def neighbor_edge(self, neighbor, duality=False):
        if duality:
            return [edge for edge in self.__edges if edge.opposite(self)==neighbor]
        else:
            for edge in self.__edges:
                if edge.opposite(self) == neighbor:
                    return edge

    def degree(self, neighbor=False):
        if neighbor:
            return len(self.neighbors(id=False))
        else:
            return len(self.__edges)

    def send_message(self, neighbor, message, duality=False, id=True):
        nei = self.__id_to_neighbor(neighbor) if id else neighbor
        if (duality == False) and (nei in self.__nei_to_edge):
            self.inject_message(self.__nei_to_edge[nei], message)
        else:
            for edge in self.__edges:
                if edge.opposite(self) == nei:
                    self.inject_message(edge, message)

    def bloadcast(self, message, recursive=False, without=[], id=True):
        to_neighbors = filter(lambda node: node not in without, self.neighbors(id=id))
        if recursive:
            for neighbor, msg in zip(to_neighbors, message):
                self.send_message(neighbor, msg, id=id)
        else:
            for neighbor in to_neighbors:
                self.send_message(neighbor, message, id=id)

    def flooding(self, message):
        for edge in self.__edges:
            self.inject_message(edge, message)

    def inject_message(self, edge, message):
        msg = message if isinstance(message, AbstractMessage) else make_message(message)
        if message != None:
            edge.inject(self, msg)


    def receive_message(self, edge, abstract_message):       # TODO refactoring this implement is vulnerable
        self.__received.append((edge, abstract_message.message()))

    def round_counter(self, initial=0):
        c = initial - 1
        def count():
            nonlocal c
            c += 1
            return c
        return count

    def frame_update(self, t, synchronizable=False):
        if synchronizable:
            self.synch_update(self.__round_counter(), list(self.__received))
            self.__received.clear()

    def synch_update(self, round, message_tuples):
        '''
        `message_tuples = [(edge, message), ...]` in order of arrival
        in synchronized network, node can send only 1 message to 1 edge in 1 round
        '''
        pass

