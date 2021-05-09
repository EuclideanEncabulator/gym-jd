import gym
import random
import pkg_resources

import numpy as np

from gym import Env
from gym.spaces import Dict, Discrete, Box, MultiBinary
from scipy.spatial.distance import euclidean
from multiprocessing import shared_memory
from gym_jd.interface.python.injector import inject
from gym_jd.interface.python.ipc import Process
from time import sleep
from collections import deque

class JDEnv(Env):
    def __init__(self, jd_path, graphics=False, continuous=True):
        ONE_SHAPE = (1,)
        self.PSEUDO_MAX_SPEED = 300
        self.CONSIDER_NODES, self.PROXIMITY_RADIUS = 1, 7
        self.CONTINUOUS = continuous
        self.MAX_EPISODE_STEPS = 500
        self.NODES = np.load(pkg_resources.resource_filename("extra", "nodes.npy"))

        self.steps, self.current_node, self.best_node = 0, 1, 1
        self.velocities = deque(maxlen=200)

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
            "speed": Box(low=0, high=500, shape=ONE_SHAPE),
            "velocity": Box(low=-500, high=500, shape=(3,)),
            "direction": Box(low=-1, high=1, shape=(4,)), # quaternion
            "wheel_direction": Box(low=-1, high=1, shape=ONE_SHAPE),
            # "position": Box(low=-np.inf, high=np.inf, shape=(2, 3)),
            "next_nodes": Box(low=-1000, high=1000, shape=(self.CONSIDER_NODES, 3)),
            "difference": Box(low=-1, high=1, shape=ONE_SHAPE),
            "grounded": Discrete(2),
            "wheels": MultiBinary(4),
        })

        self.process = Process(jd_path, graphics)
        sleep(5) # TODO: Move to c++, we can tell when unity has loaded
        dll_path = pkg_resources.resource_filename("extra", "jelly_drift_interface.dll")
        inject(self.process.pid, dll_path.encode("ascii"))
        sleep(0.1)
        self.reset()

    def episode_finished(self):
        max_steps_reached = self.steps > self.MAX_EPISODE_STEPS + self.current_node * 100
        self.steps = 0 if max_steps_reached else self.steps + 1

        return max_steps_reached

    def reset(self):
        if self.current_node > self.best_node: self.best_node = self.current_node
        self.position, self.current_node = self.NODES[0], 1

        self.perform_action(reset=True)
        
        return self.get_observation(wait=False)

    def perform_action(self, wait=True, reset: bool=False, steering: float=0.0, throttle: float=1., braking: int=0):
        self.process.write({
            "reset": reset,
            "steering": steering if self.CONTINUOUS else steering - 1,
            "throttle": throttle if self.CONTINUOUS else throttle - 1,
            "braking": 0# int(braking >= 0.5)
        }, wait)

    def get_observation(self, wait=True):
        observation = self.process.read(wait)

        self.old_position, self.current_position = self.position, observation["position"]

        observation["grounded"] = int(observation["grounded"][0])
        observation["next_nodes"] = self.NODES[self.current_node:self.current_node + self.CONSIDER_NODES] - self.current_position # Polar co-ordinates
        observation["speed"] = observation["speed"][0]
        observation["wheels"] = np.array([observation["wheel_1"][0], observation["wheel_2"][0], observation["wheel_3"][0], observation["wheel_4"][0]])

        del observation["position"]

        car_node_direction = self.NODES[self.current_node] - self.current_position
        car_node_magnitude, velocity_magnitude = np.linalg.norm(car_node_direction), np.linalg.norm(observation["velocity"])

        self.velocities.append(observation["velocity"])

        # Get difference in car direction/node
        if car_node_magnitude != 0 and velocity_magnitude != 0:
            observation["difference"] = np.dot(car_node_direction / car_node_magnitude, observation["velocity"] / velocity_magnitude)
        else: observation["difference"] = 0

        return observation

    def step(self, action):
        action.update({name: value[0] for name, value in action.items() if type(value) == np.ndarray and len(value) == 1})
        self.perform_action(**action)
        observation = self.get_observation()

        node_distance = euclidean(self.NODES[self.current_node], self.current_position)
        velocity_mean = np.mean(np.array(self.velocities))

        distance_rating = np.reciprocal(node_distance) if node_distance <= 10 else 0
        direction_rating = observation["difference"] if observation["difference"] != 0 else 1
        surface_rating = - sum(observation["wheels"]) * 0.2
        throttle_rating = (action["throttle"]) ** 2 if action["throttle"] > 0 and surface_rating == 0 else 0
        velocity_rating = -velocity_mean if velocity_mean < 0 and surface_rating == 0 else velocity_mean * 0.2

        reward = direction_rating * self.current_node + distance_rating + velocity_rating + surface_rating

        # Heavily reward going to node
        if node_distance <= self.PROXIMITY_RADIUS:
            print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            self.current_node += 1
            self.velocities.clear()

            reward = (self.current_node * velocity_rating) ** 2 if velocity_rating > 1 else self.current_node ** 2

        if self.steps % 100 == 0:
            print(f"STEP {self.steps}")
            print("distance rating", distance_rating)
            print("direction rating", direction_rating)
            print("surface rating", surface_rating)
            print("throttle_rating", throttle_rating)
            print("velocity rating", velocity_rating)
            print("reward", reward)
            print()

        info = {} # extra info for debugging
        return observation, reward, self.episode_finished(), info

    # Display a single game on screen
    # TODO
    def render(self):
        pass