#pragma once

#include "unity.hpp"
#include <windows.h>
#include <string>

namespace objects
{
	bool initialize();

	uintptr_t find_object(std::string name, uintptr_t offset, uint32_t limit);

	template <typename T>
	T* find_active_object(std::string name)
	{
		return reinterpret_cast<T*>(find_object(name, 0x18, 500));
	}

	template <typename T>
	T* find_tagged_object(std::string name)
	{
		return reinterpret_cast<T*>(find_object(name, 0x8, 500));
	}

	unity::vector3 get_position(uintptr_t transform);
	unity::quaternion get_rotation(uintptr_t transform);
	unity::quaternion get_lookat_rotation(unity::vector3 forward, unity::vector3 upwards);
	void set_position(uintptr_t rigidbody, unity::vector3 position);
	void set_rotation(uintptr_t rigidbody, unity::quaternion rotation);

	bool set_time_scale(float time_scale);
}