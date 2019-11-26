# from dimulator.node import UndirectedNode
# from dimulator.graph import UndirectedGraph
# from dimulator.daemon import FairDaemon
# from dimulator.layout import antigravity_node_layout, degree_base_edge_layout
# # from dimulator.algorithms.color_reduce import ColorReduceNode

# import os

# import numpy as np
# import matplotlib.pyplot as plt

# class ColoringStrongNode(UndirectedNode):
#     CMAP = plt.get_cmap('gist_rainbow')

#     def __init__(self, id=None):
#         super().__init__(id=id)
#         self.c = id
#         self.induced_nc = {}
#         self.recursive_arguments = []
#         self.recursive_return = id
#         self.max_degree = 1
#         self.coloring_round = 0
#         self.coloring_times = 0
#         self.color_reduce_round = 0
#         self.coloring_x = None

#     def initialize(self, n, max_degree):
#         self.n = n
#         self.max_degree = max_degree

#     def make_aveilable_color(self, n, max_degree):      # for animation
#         self.initial_color = list(ColoringNode.CMAP(i/n) for i in range(n+max_degree+1))
#         self.aveilable_color = list(ColoringNode.CMAP(i/max_degree) for i in range(2 *(max_degree + 1)+1))

#     def synch_update(self, round, message_tuples):
#         if round == self.coloring_round:
#             self.x = self.coloring(round, message_tuples)
#             self.color_reduce_round = 0
#         if self.x != 'end':
#             self.color_reduce_induced(self.color_reduce_round, message_tuples, self.x)
#             self.color_reduce_round += 1

#     def coloring(self, round, message_tuples):
#         if round == 0:
#             if self.bin_id()[-1].endswith('1'):


#     def bin_id(self):
#         return format(self.identifier(), 'b').zfill(len(format(self.n, 'b')))

#     def color_reduce_induced(self, round, message_tuples, x):
#         if round == 0:
#             self.induced_nc.setdefault(x, []).extend(m[0] for e, m in message_tuples if m[1]==x)
#             self.bloadcast(self.make_message((self.c, x), color=self.color))
#         else:
#             self.induced_nc.setdefault(x, []).extend(m[0] for e, m in message_tuples if m[1]==x)
#             if self.c == round:
#                 c = self.induced_min_color(x)
#                 self.recursive_return = c
#                 x_suffix = int(x[-1])        # 0 or 1
#                 self.color = self.aveilable_color[(c-1)+(self.max_degree+1)*x_suffix]      # for animation
#                 self.bloadcast(self.make_message((c, x), color=self.color))
#                 if message_tuples: print(f'id{self.identifier()} induced {x}({self.bin_id()}), choose {c}, induced neighbor color {self.induced_nc}, received {message_tuples}')



#     def induced_min_color(self, x):    # return minimum color not in self.nc (larger than or equal 1):
#         i = 1
#         for c in sorted(self.induced_nc.get(x, [])):   # sort make O(n log n)
#             if i < c:
#                 return i
#             else:
#                 i = c + 1
#         else:
#             return i




# def animate_coloring_strong(n=15, frames=None):
#     # make node
#     nodes = list(ColoringNode(id=i) for i in range(n))

#     # make graph and set node
#     graph = UndirectedGraph(nodes=nodes)

#     # compute node position
#     pos = antigravity_node_layout(nodes)

#     # make and set edge
#     for u, v, dist in degree_base_edge_layout(pos):
#         # graph.connect_undirected_edge(u, v, weight=min(20, 300/(1+np.exp(-(3*dist-5)))))
#         graph.connect_undirected_edge(u, v, weight=6)

#     # set max degree as initial knowledge
#     for node in nodes:
#         node.max_degree = graph.max_degree()

#     ### this information use only for animation ###
#     for node in nodes:
#         node.make_aveilable_color(graph.n(), graph.max_degree())

#     # initialize give node n
#     for node in nodes:
#         node.initialize(graph.n(), graph.max_degree())

#     # make daemon and set graph
#     daemon = FairDaemon(graph)

#     # start animation
#     # return daemon.animation(pos, weight=False, label=False, interval=100, frames=frames or n*10)

#     graph.draw_network(label=False)
#     daemon.main_loop()
#     return 'a'

# def save_coloring_strong_as_gif(n=15, frames=None, dir='./out', file='coloring_strong.gif'):
#     os.makedirs(dir, exist_ok=True)
#     ani = animate_coloring(n=n, frames=frames)
#     ani.save(f'{dir}/{file}', fps=10)