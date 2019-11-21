from dimulator.node import DirectedNode, UndirectedNode
from dimulator.edge import DirectedEdge, UndirectedEdge

class AbstractGraph:
    def __init__(self):
        self.__nodes = []
        self.__edges = []

    def nodes(self):
        return list(self.__nodes)

    def edges(self):
        return list(self.__edges)

    def refresh(self):      # O(n m delta) which delta is max degree of this graph
        self.__edges.clear()
        edges = set()
        for node in self.__nodes:
            for edge in node.edges():
                if edge.node_u().connectability(edge) and edge.node_v().connectability(edge):
                    edges.add(edge)
        self.__edges.extend(edges)

    def add_node(self, node):
        self.__nodes.append(node)

    def extend_nodes(self, *nodes):
        self.__nodes.extend(nodes)

    def remove_node(self, node):
        self.__nodes.remove(node)

    def add_edge(self, edge):
        self.__edges.append(edge)

    def extend_edges(self, *nodes):
        self.__nodes.extend(nodes)

    def remove_edge(self, edge):
        edge.eject()
        self.__edges.remove(edge)

    def eject_edge(self, edge):
        edge.eject()

    def max_weight(self):
        return max(edge.weight() for edge in self.__edges)

class DirectedGraph(AbstractGraph):     # TODO everything
    def connect_directed_edge(self, from_node, to_node, weight=1):
        edge = DirectedEdge(from_node, to_node, weight=weight, connect=True)
        self.add_edge(edge)
        return edge

    def eject_between_from_and_to(self, from_node, to_node):
        for outgoing in from_node.outgoings:
            if outgoing.to_node() == to_node:
                from_node.eject_outgoing(outgoing)
        for incoming in to_node.incoming:
            if incoming.from_node() == from_node:
                to_node.eject_incoming(incoming)

class UndirectedGraph(AbstractGraph):
    def connect_undirected_edge(self, u, v, weight=1):
        edge = UndirectedEdge(u, v, weight=weight, connect=True)
        self.add_edge(edge)
        return edge

    def remove_between_u_and_v(self, u, v):
        for edge in u.edges():
            if edge.opositte() == v:
                u.remove_edge(edge)
        for edge in v.edges():
            if edge.opositte() == u:
                v.remove_edge(edge)

    def eject_between_u_and_v(self, u, v):
        for edge in u.edges():
            if edge.opositte() == v:
                u.eject_edge(edge)
        for edge in v.edges():
            if edge.opositte() == u:
                v.eject_edge(edge)