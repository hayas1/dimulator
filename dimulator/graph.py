from dimulator.node import AbstractNode, DirectedNode, UndirectedNode
from dimulator.edge import DirectedEdge, UndirectedEdge

import networkx as nx

class AbstractGraph:
    def __init__(self, nodes=None):
        self.__nodes = []
        self.__edges = []
        if nodes != None:
            self.__nodes.extend(nodes)

    def to_networkx_graph(self, directed=False, multigraph=False, weight=False):
        g = self.__select_graph(directed, multigraph)
        g.add_nodes_from(node.to_networkx_node() for node in self.nodes())
        g.add_edges_from(edge.to_networkx_edge(weight=weight) for edge in self.edges())
        return g

    def __select_graph(self, directed, multigraph):
        if directed and multigraph:
            return nx.MultiDiGraph()
        elif directed and not multigraph:
            return nx.DiGraph()
        elif not directed and multigraph:
            return nx.MultiGraph()
        elif not directed and not multigraph:
            return nx.Graph()
        else:
            raise ValueError(f'invalid input ({directed}, {multigraph}), expected boolean')

    def draw_network(self, label=True, weight=False):
        g = self.to_networkx_graph(weight=weight)
        self.draw_networkx(g, nx.spring_layout(g), label=label, weight=weight)

    # TODO refactoring these method should not belong to this class
    def draw_networkx(self, g, pos, label=True, weight=False):
        nodes, edges = self.nodes(), self.edges()

        node_dict = {'node_size': [], 'node_color': [], 'edgecolors': [], 'linewidths': [], 'alpha':[], 'label': []}
        for node in nodes:
            node_dict['node_size'].append(node.size)
            node_dict['node_color'].append(node.color)
            node_dict['edgecolors'].append(node.border_color)
            node_dict['linewidths'].append(node.border_width)
            node_dict['alpha'].append(node.transparency)
            node_dict['label'].append(node.label)

        edge_dict = {'width': [], 'edge_color': [], 'style': [], 'label': []}
        for edge in edges:
            edge_dict['width'].append(edge.width)
            edge_dict['edge_color'].append(edge.color)
            edge_dict['style'].append(edge.style)
            # edge_dict['alpha'].append(edge.transparency)
            edge_dict['label'].append(edge.label)

        nx.draw_networkx_nodes(g, pos, nodelist=nodes, node_shape=AbstractNode.SHAPE, **node_dict)
        nx.draw_networkx_edges(g, pos, edgelist=list(map(lambda e: e.to_networkx_edge(weight=False), edges)), **edge_dict)
        nx.draw_networkx_labels(g, pos)
        if label:
            nx.draw_networkx_edge_labels(g, pos, font_size=8)

    def nodes(self):
        return list(self.__nodes)

    def edges(self):
        return list(self.__edges)

    def refresh_edge(self):      # O(n m delta) which delta is max degree of this graph
        self.__edges.clear()
        edges = set()
        for node in self.__nodes:
            for edge in node.edges():
                if edge.node_u().connectability(edge) and edge.node_v().connectability(edge):
                    edges.add(edge)
        self.__edges.extend(edges)

    def add_node(self, node):
        self.__nodes.append(node)

    def extend_nodes(self, nodes):
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
        return max(edge.weight for edge in self.__edges)

    def max_degree(self):
        return max(node.dgree() for node in self.__nodes)

class DirectedGraph(AbstractGraph):     # TODO everything
    def to_networkx_graph(self, multigraph=False, weight=False):
        return super().to_networkx_graph(directed=True, multigraph=multigraph, weight=weight)

    def connect_directed_edge(self, from_node, to_node, weight=10):
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
    def to_networkx_graph(self, multigraph=False, weight=False):
        return super().to_networkx_graph(directed=False, multigraph=multigraph, weight=weight)

    def connect_undirected_edge(self, u, v, weight=10, duality=False, selfloop=False):
        no_same_path = all(not edge.same_path(u, v) for edge in self.edges())
        if (duality or no_same_path) and not (u==v and selfloop==False):
            edge = UndirectedEdge(u, v, weight=weight, connect=True)
            self.add_edge(edge)
            return edge
        else:
            return None

    def remove_between_u_and_v(self, u, v):
        for edge in u.edges():
            if edge.opposite(u) == v:
                self.remove_edge(edge)
        for edge in v.edges():
            if edge.opposite(v) == u:
                self.remove_edge(edge)

    def eject_between_u_and_v(self, u, v):
        for edge in u.edges():
            if edge.opposite(u) == v:
                self.eject_edge(edge)
        for edge in v.edges():
            if edge.opposite(v) == u:
                self.eject_edge(edge)