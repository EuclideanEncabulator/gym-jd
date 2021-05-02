#include <Windows.h>
#include <stdio.h>
#include <iostream>
#include <thread>
#include <chrono>

#include "ipc.hpp"
#include "objects.hpp"
#include "jelly_drift.hpp"

void start()
{
	AllocConsole();
	freopen_s((FILE**)stdin, "CONIN$", "r", stdin);
	freopen_s((FILE**)stdout, "CONOUT$", "w", stdout);

	if (!ipc::initialize())
	{
		printf("failed to initialize ipc.\n");
		return;
	}

	if (!objects::initialize())
	{
		printf("failed to initialize objects.\n");
		return;
	}

	auto game_controller = objects::find_active_object<jelly_drift::game_controller>("GameController");
	auto game_state = objects::find_active_object<jelly_drift::game_state>("GameState");
	auto car = reinterpret_cast<jelly_drift::car*>(game_controller->current_car->mono_object->game_object->real_object->object);

	objects::set_time_scale(0.0f);

	using namespace std::chrono_literals;

	while (true)
	{
		WaitForSingleObject(ipc::python_mutex, INFINITE);

		if (ipc::python_buffer->reset)
		{
			game_state->reset = true;
			std::this_thread::sleep_for(100ms);
			car = reinterpret_cast<jelly_drift::car*>(game_controller->current_car->mono_object->game_object->real_object->object);
			continue;
		}

		car->throttle = ipc::python_buffer->throttle;
		car->steering = ipc::python_buffer->steering;
		car->braking = ipc::python_buffer->braking;

		auto time = std::chrono::steady_clock::now() + 33ms; // 30fps
		objects::set_time_scale(1.0f);
		std::this_thread::sleep_until(time);
		objects::set_time_scale(0.0f);

		ReleaseMutex(ipc::python_mutex);

		WaitForSingleObject(ipc::game_mutex, INFINITE);

		ipc::game_buffer->direction = objects::get_rotation(car->centre_of_mass);
		ipc::game_buffer->position = objects::get_position(car->centre_of_mass);
		ipc::game_buffer->speed = car->speed;
		ipc::game_buffer->grounded = car->grounded;
		ipc::game_buffer->wheel_direction = car->steer_angle;

		ReleaseMutex(ipc::game_mutex);
	}
}

BOOL WINAPI DllMain(HINSTANCE dll_instance, DWORD reason, LPVOID reserved)
{
	if (reason == DLL_PROCESS_ATTACH)
		std::thread(start).detach();

	return TRUE;
}