import numpy as np

from scipy.spatial.distance import cdist
class NodeFinder():
    def __init__(self, boundaries, nodes_to_check=10, max_visible_distance=20, node_threshold=7.5):
        self.BOUNDARIES = boundaries
        self.NODES = (boundaries[:, 1] + boundaries[:, 0]) / 2
        self.MAX_VISIBLE_DISTANCE, self.NODES_TO_CHECK = max_visible_distance ** 2, nodes_to_check // 2
        self.NODE_THRESHOLD = node_threshold ** 2
        
        self.reset()

    # Gets co-ordinates of closeby boundaries whilst counting penetrations
    def get_nearby_boundaries(self, current_position):
        # Consider points around the previously closest node
        lower_bound = max(self.nearest_pair - self.NODES_TO_CHECK,  0)
        upper_bound = min(self.nearest_pair + self.NODES_TO_CHECK, self.NODES.size - 1)

        distances = cdist(self.NODES[lower_bound:upper_bound], [current_position], metric="sqeuclidean")

        # If close enough to current node, count all previous as completed
        if np.any(distances): self.nearest_pair = lower_bound + distances.argmin()
        if self.nearest_pair >= self.target_node and distances[self.nearest_pair - lower_bound] <= self.NODE_THRESHOLD:
            self.penetrations = self.nearest_pair - self.target_node + 1
            self.target_node += self.penetrations
            self.steps_since_node = 0
        else:
            self.penetrations = 0
            self.steps_since_node += 1

        # Return boundaries padded to the right size
        boundaries = self.BOUNDARIES[lower_bound:upper_bound][(distances <= self.MAX_VISIBLE_DISTANCE).squeeze()]
        return np.concatenate((
            np.zeros((2 * self.NODES_TO_CHECK - len(boundaries), 2, 3)),
            boundaries
        ))

    def reset(self):
        self.nearest_pair, self.target_node = 0, 0
        self.penetrations, self.steps_since_node = 0, 0
