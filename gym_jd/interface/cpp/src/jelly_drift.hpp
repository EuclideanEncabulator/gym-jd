#pragma once

#include <cstdint>

#include "unity.hpp"

namespace jelly_drift
{
	struct car
	{
		uint8_t pad0[0x18];
		uintptr_t rigid_body;
		uintptr_t centre_of_mass;
		uint8_t pad28[0x44];
		float steering;
		float throttle;
		bool braking;
		uint8_t pad75[0x3B];
		bool grounded;
		uint8_t padB1[0x23];
		float steer_angle;
	};

	struct game_controller
	{
		uint8_t pad0[0x28];
		unity::object* current_car;
	};
};