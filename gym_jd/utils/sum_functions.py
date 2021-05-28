from inspect import signature
from typing import MutableSequence
from collections import Callable

class SumFuncs(Callable):
    def __init__(self, *funcs) -> None:
        get_arguments = lambda func : signature(func).parameters.keys()
        self.funcs, self.weights = zip(*(func if isinstance(func, MutableSequence) else (func, 1) for func in funcs))
        self.arguments = list(map(get_arguments, self.funcs))

    def __call__(self, *args, **superset):
        intersection = lambda subset : {key: superset[key] for key in subset}
        intersections = (intersection(subset) for subset in self.arguments)

        return sum(func(*args, **kwargs) * weight for func, weight, kwargs in zip(self.funcs, self.weights, intersections))
