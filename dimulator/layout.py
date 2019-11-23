import numpy as np

def lim_check(*tup):
    for mi, ma in tup:
        if mi > ma:
            raise ValueError(f'max {ma} is smaller than min {mi}')

def rand_range(tup):
    lim_check(tup)
    return (tup[1] - tup[0]) * np.random.rand() + tup[0]

def distance(p1, p2):
    p1, p2 = np.array(p1), np.array(p2)
    return np.linalg.norm(p1 - p2)

def line_rad(p1, p2):
    p1, p2 = np.array(p1), np.array(p2)
    return np.arctan2(*(p2 - p1))

def antigravity_node_layout(nodes, xlim=(-1,1), ylim=(-1,1), coefficient=0.005, iterations=5):
    pos = {node: np.array((rand_range(xlim), rand_range(ylim))) for node in nodes}
    for _ in range(iterations):
        for node, p in pos.items():
            node_force = np.sum(coefficient / distance(p, pother)**2 * (p - pother) for other, pother in pos.items() if all(np.not_equal(p, pother)))
            xmin_force = coefficient / distance(p, (xlim[0], p[1]))**3 * (p - np.array(xlim[0], p[1]))
            xmax_force = coefficient / distance(p, (xlim[1], p[1]))**3 * (p - np.array(xlim[1], p[1]))
            ymin_force = coefficient / distance(p, (ylim[0], p[0]))**3 * (p - np.array(ylim[0], p[0]))
            ymax_force = coefficient / distance(p, (ylim[1], p[0]))**3 * (p - np.array(ylim[1], p[0]))
            central_gravity = coefficient / distance(p, (np.mean(xlim), np.mean(ylim)))**2 * (np.array(np.mean(xlim), np.mean(ylim)) - p)
            pos[node] += node_force + xmin_force + xmax_force + ymin_force + ymax_force + central_gravity
            if not ((xlim[0] < pos[node][0] < xlim[1]) and (ylim[0] < pos[node][1] < ylim[1])):
                pos[node] = np.array((rand_range(xlim), rand_range(ylim)))
    return pos

def degree_base_edge_layout(pos, pieces=5, threshold=1.25):
    edges = []
    for node in pos.keys():
        piecenodes = [node] * pieces
        for other in pos.keys():
            if node == other:
                continue
            piece = int((line_rad(pos[node], pos[other])+np.pi) / (2 * np.pi / pieces))
            piecenodes[piece] = other if piecenodes[piece]==node or (distance(pos[node], pos[other]) < distance(pos[node], pos[piecenodes[piece]])) else piecenodes[piece]
        min_dist = np.mean([distance(pos[node], pos[neighbor]) for neighbor in piecenodes if node != neighbor])
        edges.extend((node, neighbor, distance(pos[node], pos[neighbor])) for neighbor in piecenodes if (node != neighbor) and (distance(pos[node], pos[neighbor]) < min_dist * threshold))
    return edges

