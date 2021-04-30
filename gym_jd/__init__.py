from gym.envs.registration import register

register(
    id='jd-v0',
    entry_point='gym_jd.envs:FooEnv',
)