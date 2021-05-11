import numpy as np

from numpy.linalg import norm
class NodeFinder():
    def __init__(self, nodes, max_visible_distance=20, node_threshold=1, max_nodes=20):
        self.NODES = nodes
        self.MAX_VISIBLE_DISTANCE, self.MAX_NODES = max_visible_distance, max_nodes
        self.NODE_THRESHOLD = node_threshold
        
        self.reset()

    def valid_nodes(self, distances, lower_bound):
        self.penetrations = 0
        valid_distances = distances <= self.MAX_VISIBLE_DISTANCE
        upper_valid_distances = valid_distances[:self.nearest_pair]

        if np.any(valid_distances):
            self.nearest_pair = lower_bound + distances.argmin()

        if np.any(upper_valid_distances):
            penetrated_nearest_pair = distances[self.nearest_pair - lower_bound] <= self.NODE_THRESHOLD
            penetrated_single_node = self.nearest_pair == self.target_node and penetrated_nearest_pair

            if self.nearest_pair > self.target_node or penetrated_single_node:
                self.steps_since_node = 0
                self.penetrations = self.nearest_pair + 1 - self.target_node if penetrated_nearest_pair else self.nearest_pair - self.target_node
                self.target_node += self.penetrations
            else: self.steps_since_node += 1
        else: self.steps_since_node += 1

        return valid_distances # boolean array

    # Get nodes around current position, assuming its close to previous
    # Returns relative co-ordinates
    def get_closest(self, current_position):
        nodes_to_check = self.MAX_NODES // 2
        lower_bound, upper_bound = self.nearest_pair - nodes_to_check, self.nearest_pair + nodes_to_check
        if lower_bound < 0: lower_bound = self.nearest_pair
        if upper_bound > self.NODES.size - 1: upper_bound = self.NODES.size - 1

        nodes = self.NODES[lower_bound:upper_bound]
        node_diff = nodes[:, 1] - nodes[:, 0]
        distances = norm(np.cross(node_diff, current_position - nodes[:, 0]) / norm(node_diff), axis=1)

        # Reset for current calculations
        nearby_nodes = nodes[self.valid_nodes(distances, lower_bound)] - current_position
        return np.concatenate((nearby_nodes, np.zeros((self.MAX_NODES - len(nearby_nodes), 2, 3))))

    def reset(self):
        self.nearest_pair, self.target_node = 0, 0
        self.penetrations, self.steps_since_node = 0, 0
