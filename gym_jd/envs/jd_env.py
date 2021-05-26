import pkg_resources

import numpy as np

from gym import Env
from gym.spaces import Dict, Discrete, Box, MultiBinary
from gym_jd.utils.nodes import NodeFinder
from gym_jd.interface.python.injector import inject
from gym_jd.interface.python.ipc import Process
from time import sleep

class JDEnv(Env):
    def __init__(self, jd_path, graphics=False, continuous=True):
        ONE_SHAPE = (1,)
        self.NODES_TO_CHECK, self.NODE_THRESHOLD = 3, 7.3
        self.PREVIOUS_VISIBLE_NODES, self.NEXT_VISIBLE_NODES = 2, 4
        self.PREVIOUS_VISIBLE_FREQUENCY, self.NEXT_VISIBLE_FREQUENCY = 1, 2
        self.CONTINUOUS = continuous
        self.MAX_IDLE_STEPS = 300
        self.NODES = NodeFinder(
            nodes_to_check=self.NODES_TO_CHECK,
            node_threshold=self.NODE_THRESHOLD,
            previous_visible_nodes=self.PREVIOUS_VISIBLE_NODES,
            next_visible_nodes=self.NEXT_VISIBLE_NODES,
            previous_visible_frequency=self.PREVIOUS_VISIBLE_FREQUENCY,
            next_visible_frequency=self.NEXT_VISIBLE_FREQUENCY
        )

        num_nodes = self.PREVIOUS_VISIBLE_NODES * self.PREVIOUS_VISIBLE_FREQUENCY + self.NEXT_VISIBLE_NODES * self.NEXT_VISIBLE_FREQUENCY

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
            "road_boundaries": Box(low=-1000, high=1000, shape=(num_nodes, 2, 3)),
            "grounded": MultiBinary(1),
            "wheels": MultiBinary(4),
        })

        self.process = Process(jd_path, graphics)
        sleep(5) # TODO: Move to c++, we can tell when unity has loaded
        dll_path = pkg_resources.resource_filename("extra", "jelly_drift_interface.dll")
        inject(self.process.pid, dll_path.encode("ascii"))
        sleep(0.1)

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
        observation["road_boundaries"] = self.NODES.get_nearby_boundaries(observation["position"])

        self.position = observation["position"]

        del observation["position"], observation["speed"]

        return observation

    def step(self, action):
        action.update({name: value[0] for name, value in action.items() if type(value) == np.ndarray and len(value) == 1})
        self.perform_action(**action)
        observation = self.get_observation()
        
        node_rating = self.NODES.penetrations * self.NODES.target_node
        surface_rating = -sum(observation["wheels"]) * 0.2

        reward = node_rating + surface_rating

        info = {"position": self.position} # extra info for debugging
        done = self.NODES.steps_since_node > self.MAX_IDLE_STEPS

        return observation, reward, done, info

    # Visualisation is all pre-set
    def render(self):
        pass
