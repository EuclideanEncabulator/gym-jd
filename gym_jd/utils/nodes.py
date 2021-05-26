import numpy as np

from scipy.spatial.distance import cdist
class NodeFinder():
    def __init__(self, boundaries, nodes_to_check=3, visible_nodes=20, visible_frequency=1, node_threshold=7.5):
        self.BOUNDARIES = boundaries
        self.NODES = (boundaries[:, 1] + boundaries[:, 0]) / 2
        self.NODES_TO_CHECK, self.VISIBLE_NODES = nodes_to_check, visible_nodes // 2
        self.VISIBLE_FREQUENCY, self.NODE_THRESHOLD = visible_frequency, node_threshold ** 2
        
        self.reset()

    # Gets co-ordinates of closeby boundaries whilst counting penetrations
    def get_nearby_boundaries(self, current_position):
        # Consider points around the previously closest node
        lower_bound = max(self.nearest_pair - self.NODES_TO_CHECK,  0)
        upper_bound = min(self.nearest_pair + self.NODES_TO_CHECK, len(self.NODES) - 1)

        # Find the closest node
        # Using four reference points
        distances = cdist(self.NODES[[lower_bound, self.nearest_pair, upper_bound, self.target_node]], [current_position], metric="sqeuclidean")

        if np.any(distances):
            index = distances.argmin()

            if index == 0:
                self.nearest_pair = lower_bound
            elif index == 2:
                self.nearest_pair = upper_bound
            elif index == 3:
                self.nearest_pair = self.target_node

        # If close enough to current node, count all previous as completed
        # Accounts for car moving through multiple nodes at once or re-entering track
        if self.nearest_pair >= self.target_node and distances[index] <= self.NODE_THRESHOLD:
            self.penetrations = self.nearest_pair - self.target_node + 1
            self.target_node += self.penetrations
            self.steps_since_node = 0
        else:
            self.penetrations = 0
            self.steps_since_node += 1

        # Return boundaries padded to the right size
        # Consider points around the previously closest node
        lower_bound = max(self.nearest_pair - self.VISIBLE_NODES,  0)
        upper_bound = min(self.nearest_pair + self.VISIBLE_NODES, len(self.NODES) - 1)

        boundaries = self.BOUNDARIES[lower_bound:upper_bound:self.VISIBLE_FREQUENCY] - current_position
        return np.concatenate((
            np.zeros((2 * self.VISIBLE_NODES // self.VISIBLE_FREQUENCY - len(boundaries), 2, 3)),
            boundaries
        ))

    def reset(self):
        self.nearest_pair, self.target_node = 0, 0
        self.penetrations, self.steps_since_node = 0, 0
