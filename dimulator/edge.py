class Edge:
    def __init__(self, u, v, weight=1, color='k', label=None):
        self.__u = u
        self.__v = v
        self.__weight = weight
        self.width = 1
        self.color = 'k'
        self.style = 'solid'
        self.alpha = None
        self.label = label

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
            raise ValueError(f'the node {node} is not connected this edge ({self.__u}, {self.__v})')

class DirectedEdge(Edge):
    def __init__(self, from_, to, weight=1):
        super().__init__(from_, to, weight)
        from_.add_edge(self)
    
    def inject(self, message):
        pass
        

class UndirectedEdge(Edge):
    def __init__(self, u, v, weight=1):
        super().__init__(u, v, weight)
        self.__uv = DirectedEdge(u, v)
        self.__vu = DirectedEdge(v, u)
        