import gym

import numpy as np

from gym import Env
from gym.spaces import Dict, Discrete, Box
from scipy.spatial.distance import cdist
from multiprocessing import shared_memory

class JDEnvironment(Env):
    def __init__(self, jd_path):
        ONE_SHAPE = (1,)

        # TODO: Check whether mix of continuous and discrete actions works
        self.action_space = Dict({
            "steering": Box(low=-1, high=1, shape=ONE_SHAPE),
            "braking": Discrete(2),
            "throttle": Box(low=-1, high=1, shape=ONE_SHAPE)
        })
        self.observation_space = Dict({
            "speed": Box(low=0, high=np.inf, shape=ONE_SHAPE),
            "direction": Box(low=-1, high=1, shape=(4,)), # quaternion
            "position": Box(low=-np.inf, high=np.inf, shape=(2,)), # get coord bounds
            "grounded": Discrete(2),
            "wheel_direction": Box(low=-1, high=1, shape=ONE_SHAPE), # get rotation bounds
            "next_nodes": Box(low=-np.inf, high=np.inf, shape=(3, 3)) # get coord bounds
        })

        # TODO: Start Jelly Drift
        # TODO: Inject DLL

        # TODO: Set up shared processes for Jelly Drift
        shared_memory.SharedMemory(name="jd_rl", size=4, create=True)
        shared_memory.SharedMemory(name="jd_game", size=101, create=True)

    def reset(self):
        # TODO: Start a new episode from the beginning
        self.nodes = np.load("config/nodes.npy")

        # return observation
        pass

    def step(self, action):
        PSEUDO_MAX_SPEED = 300
        CONSIDER_NODES, PROXIMITY_RADIUS = 5, 5

        # TODO: Perform action

        # TODO: Get reaal observation (state)
        observation = {"position": 0, "next_nodes": 0, "speed": 0} # TODO: REMOVE
        distances, index = cdist(observation["position"], self.nodes[:CONSIDER_NODES]), np.arrange(CONSIDER_NODES)
        path_proximity = (distances * index ^ 2).reciprocal().sum()

        # Remove currently passed nodes
        # Test wether episode finished
        self.nodes = np.delete(self.nodes, (distances < PROXIMITY_RADIUS).nonzero())
        done = self.nodes.size != 0

        reward = (observation["speed"] / PSEUDO_MAX_SPEED) * path_proximity

        info = {} # extra info for debugging
        return observation, reward, done, info

    # Display a single game on screen
    def render(self):
        pass
