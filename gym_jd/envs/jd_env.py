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
    def __init__(self, jd_path, graphics=False):
        ONE_SHAPE = (1,)

        self.action_space = Dict({
            "steering": Box(low=-1, high=1, shape=ONE_SHAPE),
            "braking": Discrete(2),
            "throttle": Box(low=-1, high=1, shape=ONE_SHAPE)
        })
        self.observation_space = Dict({
            "speed": Box(low=0, high=np.inf, shape=ONE_SHAPE),
            "direction": Box(low=-1, high=1, shape=(4,)), # quaternion
            "position": Box(low=-np.inf, high=np.inf, shape=(2,)),
            "grounded": Discrete(2),
            "wheel_direction": Box(low=-1, high=1, shape=ONE_SHAPE),
            "next_nodes": Box(low=-np.inf, high=np.inf, shape=(3, 3))
        })

        self.nodes = np.load(pkg_resources.resource_filename("extra", "nodes.npy"))

        self.process = Process(jd_path, graphics)
        sleep(5) # TODO: Move to c++, we can tell when unity has loaded
        dll_path = pkg_resources.resource_filename("extra", "jelly_drift_interface.dll")
        inject(self.process.pid, dll_path.encode("ascii"))
        sleep(0.1)
        self.reset()

    def reset(self):
        self.perform_action(reset=True)
        return self.get_observation(wait=False)

    def perform_action(self, wait=True, reset: bool=False, steering: float=0.0, throttle: float=1., braking: bool=False):
        self.process.write({
            "reset": reset,
            "steering": steering,
            "throttle": throttle,
            "braking": braking
        }, wait)

    def get_observation(self, wait=True):
        return self.process.read(wait)

    def step(self, action):
        PSEUDO_MAX_SPEED = 300
        CONSIDER_NODES, PROXIMITY_RADIUS = 1, 5

        action.update({name: value[0] for name, value in action.items() if type(value) == np.ndarray and len(value) == 1})
        self.perform_action(**action)
        observation = self.get_observation()
        observation["speed"] = observation["speed"][0]

        distances, index = cdist([observation["position"]], self.nodes[:CONSIDER_NODES]), np.arange(CONSIDER_NODES)
        path_proximity = np.reciprocal(distances * (index + 1) ** 2).sum()

        # Remove currently passed nodes
        # Test wether episode finished
        self.nodes = np.delete(self.nodes, (distances < PROXIMITY_RADIUS).nonzero(), axis=0)
        done = self.nodes.size != 0

        reward = (observation["speed"] / PSEUDO_MAX_SPEED) * path_proximity

        info = {} # extra info for debugging
        return observation, reward, done, info

    # Display a single game on screen
    # TODO
    def render(self):
        pass
