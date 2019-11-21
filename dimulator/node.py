class Node:
    def __init__(self, id=None, size=300, color='#1f78b4'):
        self.__id = id
        self.size = size
        self.color = color

        self.__max_port = 0
        self.__neighbors = {}

    @property
    def identifier(self):
        return self.__id

    @property
    def neighbors(self):
        return self.__neighbors.values()

    def neighbor(self, port):
        return self.__neighbors

    def set_neighbor(self, port, node):
        self.__neighbors[port] = node

    def remove_neighbor(self, node):
        for p, n in self.__neighbors.items():
            if n == node:
                return self.__neighbors.pop(p)
        else:
            raise ValueError(f'the node {node} is not neighor')

    def add_neighbor(self, node):
        for i in range(self.__max_port):
            pass #TODO
