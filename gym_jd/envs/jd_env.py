import gym
import random
import pkg_resources

import numpy as np

from gym import Env
from gym.spaces import Dict, Discrete, Box, MultiBinary
from multiprocessing import shared_memory
from gym_jd.utils.nodes import NodeFinder
from gym_jd.interface.python.injector import inject
from gym_jd.interface.python.ipc import Process
from time import sleep
from collections import deque

class JDEnv(Env):
    def __init__(self, jd_path, graphics=False, continuous=True):
        ONE_SHAPE = (1,)
        self.PSEUDO_MAX_SPEED = 300
        self.MAX_VISIBLE_NODES, self.PROXIMITY_RADIUS = 20, 1
        self.CONTINUOUS = continuous
        self.MAX_IDLE_STEPS = 100
        self.NODES = NodeFinder(
            np.load(pkg_resources.resource_filename("extra", "nodes.npy")),
            node_threshold=self.PROXIMITY_RADIUS,
            max_nodes=self.MAX_VISIBLE_NODES
        )

        self.velocities = deque(maxlen=100)

        self.action_space = Dict({
            "steering": Box(low=-1, high=1, shape=ONE_SHAPE),
            # "braking": Box(low=0, high=1, shape=ONE_SHAPE),
            "throttle": Box(low=-1, high=1, shape=ONE_SHAPE)
        }) if self.CONTINUOUS else Dict({
            "steering": Discrete(3),
            # "braking": Discrete(2),
            "throttle": Discrete(3)
        })
        self.observation_space = Dict({
            "velocity": Box(low=-500, high=500, shape=(3,)),
            "direction": Box(low=-1, high=1, shape=(4,)), # quaternion
            "wheel_direction": Box(low=-1, high=1, shape=ONE_SHAPE),
            "road_boundaries": Box(low=-1000, high=1000, shape=(self.MAX_VISIBLE_NODES, 2, 3)),
            "grounded": MultiBinary(1),
            "wheels": MultiBinary(4),
        })

        self.process = Process(jd_path, graphics)
        sleep(5) # TODO: Move to c++, we can tell when unity has loaded
        dll_path = pkg_resources.resource_filename("extra", "jelly_drift_interface.dll")
        inject(self.process.pid, dll_path.encode("ascii"))
        sleep(0.1)

    def episode_finished(self):
        max_steps_reached = self.NODES.steps_since_node > self.MAX_IDLE_STEPS

        return max_steps_reached

    def reset(self):
        self.perform_action(reset=True)
        self.NODES.reset()
        
        return self.get_observation(wait=False)

    def perform_action(self, wait=True, reset: bool=False, steering: float=0., throttle: float=1., braking: int=0):
        self.process.write({
            "reset": reset,
            "steering": steering if self.CONTINUOUS else steering - 1,
            "throttle": throttle if self.CONTINUOUS else throttle - 1,
            "braking": 0# int(braking >= 0.5)
        }, wait)

    def get_observation(self, wait=True):
        observation = self.process.read(wait)

        observation["grounded"] = observation["grounded"][0]
        observation["wheels"] = np.array([observation["wheel_1"][0], observation["wheel_2"][0], observation["wheel_3"][0], observation["wheel_4"][0]])
        observation["road_boundaries"] = self.NODES.get_closest(observation["position"])

        self.velocities.append(observation["velocity"])

        del observation["position"], observation["speed"]

        return observation

    def step(self, action):
        action.update({name: value[0] for name, value in action.items() if type(value) == np.ndarray and len(value) == 1})
        self.perform_action(**action)
        observation = self.get_observation()
        
        velocity_mean = np.mean(np.array(self.velocities))

        node_rating = self.NODES.penetrations
        surface_rating = -sum(observation["wheels"]) * 0.2
        throttle_rating = (action["throttle"]) ** (1 / 2) if action["throttle"] > 0 and surface_rating == 0 else 0
        velocity_rating = -velocity_mean if velocity_mean < 0 and surface_rating == 0 else velocity_mean * 0.2

        reward = node_rating + throttle_rating + surface_rating

        # print("node rating", node_rating)
        # print("surface rating", surface_rating)
        # print("throttle_rating", throttle_rating)
        # print("velocity rating", velocity_rating)
        # print("reward", reward)
        # print()

        info = {} # extra info for debugging
        return observation, reward, self.episode_finished(), info

    # Display a single game on screen
    # TODO
    def render(self):
        pass
