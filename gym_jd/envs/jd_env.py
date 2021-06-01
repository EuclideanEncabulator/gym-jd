import numpy as np

from gym import Env
from gym.spaces import Dict, Discrete, Box, MultiBinary
from gym_jd.utils.nodes import NodeFinder
from gym_jd.interface.python.managed_process import ManagedProcess
from typing import Callable

class JDEnv(Env):
    def __init__(self, jd_path, nodes: NodeFinder, reward_func: Callable, max_idle_steps:int=300, graphics: bool=False, resolution: int=1080, continuous: bool=True):
        self.CONTINUOUS = continuous
        self.MAX_IDLE_STEPS = max_idle_steps
        self.NODES = nodes

        ONE_SHAPE = (1,)

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
            "road_boundaries": Box(low=-1000, high=1000, shape=(self.NODES.NUM_NODES, 2, 3)),
            "grounded": MultiBinary(1),
            "wheels": MultiBinary(4),
        })

        self.process = ManagedProcess(jd_path, graphics, resolution)
        self.reward_func = reward_func

    def reset(self):
        self.steps = 0
        position, lookat, upwards = self.NODES.reset()
        self.perform_action(reset=True, position=position, lookat=lookat, upwards=upwards)
        
        return self.get_observation(wait=False)

    def perform_action(self,
        wait=True,
        reset: bool=False,
        steering: float=0.,
        throttle: float=1.,
        braking: int=0,
        position=(0, 0, 0),
        lookat=(0, 0, 0),
        upwards=(0, 0, 0)
    ):
        self.process.write({
            "reset": reset,
            "steering": steering if self.CONTINUOUS else steering - 1,
            "throttle": throttle if self.CONTINUOUS else throttle - 1,
            "braking": 0,# int(braking >= 0.5)
            "force_move": reset,
            "position": position,
            "lookat": lookat,
            "upwards": upwards
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
        
        reward = self.reward_func(nodes=self.NODES, observation=observation)

        info = {"position": self.position} # extra info for debugging
        done = self.NODES.steps_since_node > self.MAX_IDLE_STEPS

        if self.NODES.target_node >= len(self.NODES.NODES):
            self.reset()

        return observation, reward, done, info

    # Visualisation is all pre-set
    def render(self):
        pass
