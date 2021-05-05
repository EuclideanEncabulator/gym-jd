from gym import ActionWrapper
from gym.spaces import MultiDiscrete
from gym.spaces import flatten_space, unflatten

# NOTE: Use this + Gym's FlattenObservation wrapper for RL libraries without dictionary space support
class FlattenAction(ActionWrapper):
    def __init__(self, env, continuous=True):
        super().__init__(env)
        self.CONTINUOUS = continuous

        # Work arounds for continuous and discrete spaces
        if self.CONTINUOUS == False:
            self.action_space = MultiDiscrete([space.n for _, space in env.action_space.spaces.items()])
            self.labels = env.action_space.spaces.keys()
        else:
            self.action_space = flatten_space(self.action_space)

    def action(self, action):
        if self.CONTINUOUS == False:
            return {key: value for key, value in zip(self.labels, action)}
        else:
            return unflatten(self.env.action_space, action)
