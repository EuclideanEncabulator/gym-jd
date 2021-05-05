# Jelly Drift Gym Environment
## AI Playing Games - Racing Time
Driving a car within a video game is a relatively easy and relaxing process for a human.
Here we try and train an AI to race a car around a race track as fast as possible!


This repository provides a Gym environment for the Unity game Jelly Drift.
It allows Python control over the Unity game.

## Instalation and Environment
To set up the Gym environment from scratch please compile the C++ code (or use precompiled DLLs), put them into the extra file and then run:
`pip install -e .`

NOTE: This Gym environment uses dictionary spaces for both observations and actions, this can be circumvented by using Gym's `FlattenObservation` and our `FlattenAction` wrapper (i.e. for RL libraries without dictionary space support)
