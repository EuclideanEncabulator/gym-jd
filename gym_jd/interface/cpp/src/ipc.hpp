#pragma once

#include "unity.hpp"
#include <windows.h>
#include <stdint.h>

namespace ipc
{
#pragma pack(show)
#pragma pack(push, 1)
	struct message_python
	{
		bool changed;
		bool reset;
		float steering, throttle;
		bool braking;
	};

	struct message_game
	{
		bool changed;
		unity::quaternion direction;
		unity::vector3 position;
		float wheel_direction, speed;
		bool grounded;
	};
#pragma pack(pop)

	bool initialize();
	message_game* game();
	message_python* python();
}