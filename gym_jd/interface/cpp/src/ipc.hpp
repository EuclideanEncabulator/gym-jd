#pragma once

#include "unity.hpp"
#include <windows.h>
#include <stdint.h>

namespace ipc
{
#pragma pack(push, 1)
	struct message_python
	{
		bool reset;
		float steering, throttle;
		bool braking;
		bool force_move;
		unity::vector3 position;
		unity::vector3 lookat;
		unity::vector3 upwards;
	};

	struct message_game
	{
		unity::quaternion direction;
		unity::vector3 position, velocity;
		float wheel_direction, speed;
		bool grounded;
		bool fr, fl, rr, rl;
	};
#pragma pack(pop)

	bool initialize();
	extern HANDLE game_mutex, python_mutex;
	extern message_python* python_buffer;
	extern message_game* game_buffer;
}