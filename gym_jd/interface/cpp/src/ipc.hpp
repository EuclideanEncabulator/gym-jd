#pragma once

#include "unity.hpp"
#include <windows.h>

namespace ipc
{
	struct message_python
	{
		bool close;
		bool w, a, s, d;
	};

	struct message_game
	{
		unity::vector3 direction, position, cur_node, next_node, wheel_direction;
		float velocity;
	};

	bool initialize();
	void write(message_game* msg);
	ipc::message_python* read();
}