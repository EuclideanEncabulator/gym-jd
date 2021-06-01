import pkg_resources

import numpy as np

from scipy.spatial.distance import cdist
from numpy.random import choice
from numpy.linalg import norm

class NodeFinder():
    def __init__(self, nodes_to_check=3, previous_visible_nodes=2, next_visible_nodes=4, previous_visible_frequency=1, next_visible_frequency=2, node_threshold=7.5):
        self.BOUNDARIES = np.load(pkg_resources.resource_filename("extra", "nodes.npy"))
        self.NODES = (self.BOUNDARIES[:, 1] + self.BOUNDARIES[:, 0]) / 2
        self.NODES_TO_CHECK, self.NODE_THRESHOLD = nodes_to_check, node_threshold ** 2

        self.PREVIOUS_VISIBLE_NODES, self.NEXT_VISIBLE_NODES = previous_visible_nodes, next_visible_nodes
        self.PREVIOUS_VISIBLE_FREQUENCY, self.NEXT_VISIBLE_FREQUENCY = previous_visible_frequency, next_visible_frequency
        self.NUM_NODES = self.PREVIOUS_VISIBLE_NODES * self.PREVIOUS_VISIBLE_FREQUENCY + self.NEXT_VISIBLE_NODES * self.NEXT_VISIBLE_FREQUENCY
        
        self.reset()

    # Gets co-ordinates of closeby boundaries whilst counting penetrations
    def get_nearby_boundaries(self, current_position):
        # Consider points around the previously closest node
        lower_bound = max(self.nearest_pair - self.NODES_TO_CHECK,  0)
        upper_bound = min(self.nearest_pair + self.NODES_TO_CHECK, len(self.NODES) - 1)

        # Find the closest node
        # Using four reference points
        distances = cdist(self.NODES[[lower_bound, self.nearest_pair, upper_bound, self.target_node]], [current_position], metric="sqeuclidean")
        self.target_distance = distances[-1][0]

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
        lower_bound = max(self.nearest_pair - self.PREVIOUS_VISIBLE_NODES * self.PREVIOUS_VISIBLE_FREQUENCY,  0)
        upper_bound = min(self.nearest_pair + self.NEXT_VISIBLE_NODES * self.NEXT_VISIBLE_FREQUENCY, len(self.NODES) - 1)

        lower_boundaries = self.BOUNDARIES[lower_bound:self.nearest_pair:self.PREVIOUS_VISIBLE_FREQUENCY] - current_position
        upper_boundaries = self.BOUNDARIES[self.nearest_pair:upper_bound:self.NEXT_VISIBLE_FREQUENCY] - current_position

        return np.concatenate((
            np.zeros((self.NUM_NODES - len(lower_boundaries) - len(upper_boundaries), 2, 3)),
            lower_boundaries,
            upper_boundaries
        ))

    def random_position(self, reference_away=1):
        # Random point within range
        index = choice(range(0, len(self.NODES) - reference_away))

        current_node, next_node = self.NODES[index], self.NODES[index + reference_away]
        current_boundary, next_boundary = self.BOUNDARIES[index], self.BOUNDARIES[index + reference_away]
        perpendicular = np.cross(next_boundary[0] - current_boundary[0], current_boundary[1] - current_boundary[0])

        return current_node + perpendicular / norm(perpendicular), next_node - current_node, perpendicular, index

    def reset(self):
        position, lookat, upwards, index = self.random_position()

        self.nearest_pair, self.target_node = index, index + 1
        self.penetrations, self.steps_since_node = 0, 0
        self.target_distance = 0

        return position, lookat, upwards
