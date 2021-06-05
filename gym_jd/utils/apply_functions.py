from inspect import signature
from typing import MutableSequence
from collections import Callable

class ApplyFuncs(Callable):
    def __init__(self, **funcs) -> None:
        get_arguments = lambda func : signature(func).parameters.keys()
        self.names, (self.funcs, self.weights) = funcs.keys(), zip(*(func if isinstance(func, MutableSequence) else (func, 1) for func in funcs.values()))
        self.arguments = list(map(get_arguments, self.funcs))

    def __call__(self, *args, **superset):
        intersection = lambda subset : {key: superset[key] for key in subset}
        intersections = (intersection(subset) for subset in self.arguments)

        return {name: func(*args, **kwargs) * weight for name, func, weight, kwargs in zip(self.names, self.funcs, self.weights, intersections)}
