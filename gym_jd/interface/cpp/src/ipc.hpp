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
	};

	struct message_game
	{
		unity::quaternion direction;
		unity::vector3 position;
		float wheel_direction, speed;
		bool grounded;
	};
#pragma pack(pop)

	bool initialize();
	extern HANDLE game_mutex, python_mutex;
	extern message_python* python_buffer;
	extern message_game* game_buffer;
}