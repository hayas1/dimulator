from dimulator.node import DirectedNode, UndirectedNode
from dimulator.edge import DirectedEdge, UndirectedEdge

class AbstractGraph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, node):
        self.nodes.append(node)

    def extend_nodes(self, nodes):
        self.nodes.extend(nodes)

    def remove_node(self, node):
        self.nodes.remove(node)

    def eject_edge(self, edge):
        edge.eject()

class DirectedGraph(AbstractGraph):     # TODO everything
    def connect_directed_edge(self, from_node, to_node, weight=1):
        edge = DirectedEdge(from_node, to_node, weight=weight, connect=True)
        self.edges.append(edge)
        return edge

    def eject_directed_edge(self, from_node, to_node):
        for outgoing in from_node.outgoings:
            if outgoing.to_node() == to_node:
                from_node.eject_outgoing(outgoing)
        for incoming in to_node.incoming:
            if incoming.from_node() == from_node:
                to_node.eject_incoming(incoming)

class UndirectedGraph(AbstractGraph):
    def connect_undirected_edge(self, u, v, weight=1):
        edge = UndirectedEdge(u, v, weight=1, connect=True)
        self.edges.append(edge)
        return edge

    def eject_undirected_edge(self, u, v, weight=1):
        for edge in u.edges():
            if edge.opositte() == v:
                u.eject_edge(edge)
        for edge in v.edges():
            if edge.opositte() == u:
                v.eject_edge(edge)