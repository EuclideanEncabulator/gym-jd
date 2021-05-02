import gym
import pkg_resources

import numpy as np

from gym import Env
from gym.spaces import Dict, Discrete, Box
from scipy.spatial.distance import cdist
from multiprocessing import shared_memory
from gym_jd.interface.python.injector import inject
from gym_jd.interface.python.ipc import Process
from time import sleep
import random

class JDEnv(Env):
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

        self.nodes = np.load(pkg_resources.resource_filename("extra", "nodes.npy"))

        self.process = Process(jd_path)
        sleep(5) # TODO: Move to c++, we can tell when unity has loaded.
        inject(self.process.pid, pkg_resources.resource_filename("extra", "jelly_drift_interface.dll"))

    def reset(self):
        # TODO: Start a new episode from the beginning
        self.nodes = np.load(pkg_resources.resource_filename("extra", "nodes.npy"))

        # return observation
        pass

    def step(self, action):
        PSEUDO_MAX_SPEED = 300
        CONSIDER_NODES, PROXIMITY_RADIUS = 5, 5

        # Get observation/state from IPC
        observation = self.process.read()

        distances, index = cdist([observation["position"]], self.nodes[:CONSIDER_NODES]), np.arange(CONSIDER_NODES)
        path_proximity = np.reciprocal(distances * (index + 1) ** 2).sum()

        # Remove currently passed nodes
        # Test wether episode finished
        self.nodes = np.delete(self.nodes, (distances < PROXIMITY_RADIUS).nonzero())
        done = self.nodes.size != 0

        observation["speed"] = observation["speed"][0] # TODO: Check whether intended
        reward = (observation["speed"] / PSEUDO_MAX_SPEED) * path_proximity

        self.process.write({
            "reset": False,
            "steering": 0.0,
            "throttle": random.random(),
            "braking": False
        })

        info = {} # extra info for debugging
        return observation, reward, done, info

    # Display a single game on screen
    def render(self):
        pass
