class Node:
    def __init__(self, id=None, size=300, color='#1f78b4', bcolor='k', bwidth=1, alpha=None, label=None):
        self.__edges = []       
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
        neighbors = ', '.join(str(nei.identifier()) for nei in self.neighbors())
        return f'id:{self.identifier()}, neighbors: {neighbors}'

    def add_edge(self, edge):
        self.__edges.append(edge)
        
    def remove_edge(self, edge):
        self.__edges.remove(edge)
        
    def neighbors(self):
        return [edge.opposite(self) for edge in self.__edges]
        
    def frame_update(self, t):
        pass
    
    def synch_update(self, t, msg):
        pass
