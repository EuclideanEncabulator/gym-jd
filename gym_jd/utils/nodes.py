import pkg_resources

import numpy as np
import numba as nb

from numpy.linalg import norm
from numba import njit, float64, int32
from numba.experimental import jitclass

@njit
def line_distance(node_pair: np.array, position: np.array):
    node_diff = node_pair[1] - node_pair[0]

    return norm(np.cross(node_diff, position - node_pair[0]) / norm(node_diff))

spec = [
    ("NODES", float64[:, :, :]),
    ("MAX_VISIBLE_DISTANCE", float64),
    ("MAX_NODES", int32),
    ("NODE_THRESHOLD", int32),
    ("penetrations", float64),
    ("target_node", int32),
    ("steps_since_node", int32),
    ("nearest_pair", int32),
    ("nearest_distance", float64),
]

@jitclass(spec)
class NodeFinder():
    def __init__(self, nodes, max_visible_distance=20, node_threshold=1, max_nodes=20):
        self.NODES = nodes
        self.MAX_VISIBLE_DISTANCE, self.MAX_NODES = max_visible_distance, max_nodes
        self.NODE_THRESHOLD = node_threshold
        
        self.reset()

    # Gets the nearest nodes in one direction
    # Assumes nodes are ordered
    def nodes_beyond(self, nodes, position, record_penetration=False):
        if record_penetration: self.penetrations = 0

        for index, node_pair in enumerate(nodes):
            point_line_distance = line_distance(node_pair, position)

            if point_line_distance > self.MAX_VISIBLE_DISTANCE or index > self.MAX_NODES // 2:
                return nodes[:index]
            else:
                if record_penetration and point_line_distance <= self.NODE_THRESHOLD:
                    self.penetrations += 1
                    self.target_node += 1
                    self.steps_since_node = 0
                elif record_penetration:
                    record_penetration = False
                    self.steps_since_node += 1
                if point_line_distance < self.nearest_distance:
                    self.nearest_pair, self.nearest_distance = index, point_line_distance

        return nodes

    # Get nodes around current position, assuming its close to previous
    # Returns relative co-ordinates
    def get_closest(self, current_position):
        nodes_to_check = self.MAX_NODES // 2
        lower_bound, upper_bound = self.nearest_pair - nodes_to_check, self.nearest_pair + nodes_to_check
        if lower_bound < 0: lower_bound = self.nearest_pair
        if upper_bound > self.NODES.size - 1: upper_bound = self.NODES.size - 1

        # Reset for current calculations
        self.nearest_pair, self.nearest_distance = 0, np.inf

        nearby_nodes = np.concatenate((
            self.nodes_beyond(self.NODES[lower_bound:self.nearest_pair], current_position),
            self.nodes_beyond(self.NODES[self.nearest_pair:upper_bound], current_position, record_penetration=True)
        )) - current_position

        return np.concatenate((nearby_nodes, np.zeros((self.MAX_NODES - len(nearby_nodes), 2, 3))))

    def reset(self):
        self.nearest_pair, self.nearest_distance = 0, np.inf
        self.target_node, self.steps_since_node = 0, 0
