import numpy as np

from gym_jd.utils.nodes import NodeFinder
from gym_jd.utils.apply_functions import ApplyFuncs
from typing import MutableSequence

class Reward(ApplyFuncs):
    def __init__(self, **funcs) -> None:
        get_func = lambda func : globals()[func] if isinstance(func, str) else func
        funcs = {name: [get_func(func[0]), func[1]] if isinstance(func, MutableSequence) else get_func(func) for name, func in funcs.items()}

        super().__init__(**funcs)

def penetrations(nodes: NodeFinder):
    return nodes.penetrations

def distance(nodes: NodeFinder):
    return np.reciprocal(nodes.target_distance)

def index(nodes: NodeFinder):
    return nodes.penetrations * nodes.target_node

def surface(observation: np.array):
    return -sum(observation["wheels"])

def static_negative(nodes: NodeFinder):
    return -1 if nodes.penetrations <= 0 else 0

def dynamic_negative(nodes: NodeFinder):
    return (1 / 1000) * np.reciprocal(nodes.target_node) - 50
