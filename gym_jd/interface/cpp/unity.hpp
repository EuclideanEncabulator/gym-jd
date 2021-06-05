#pragma once
// We need zero sized arrays as we don't know how long the strings are.
#pragma warning( disable : 4200 )

#include <windows.h>
#include <cstdint>

namespace unity
{
	struct vector3
	{
		float x, y, z;
	};

	struct quaternion
	{
		float w, x, y, z;
	};

	struct real_object
	{
		uint8_t pad0[0x28];
		void* object;
	};

	struct game_object
	{
		uint8_t pad0[0x18];
		real_object* real_object;
	};

	struct mono_object
	{
		uint8_t pad0[0x30];
		game_object* game_object;
		uint8_t pad38[0x28];
		char* name[];
	};

	struct object
	{
		uint8_t pad0[0x8];
		object* next_object;
		mono_object* mono_object;
	};

	struct load_scene_parameters
	{
		int load_scene_mode;
		int load_physics_mode;
	};

	struct manager_context
	{
		uintptr_t managers[0x18];
	};

	struct time_manager
	{
		uint8_t pad0[0xFC];
		float time_scale;
	};
}