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

	bool last_changed = false;
	auto python = ipc::python();
	auto game = ipc::game();

	while (true)
	{
		if (last_changed == python->changed)
		{
			using namespace std::chrono_literals;
			std::this_thread::sleep_for(1ms);
			continue;
		}

		last_changed = python->changed;

		game->changed = !game->changed;
		game->direction = objects::get_rotation(car->centre_of_mass);
		game->position = objects::get_position(car->centre_of_mass);
		game->speed = car->speed;
		game->grounded = car->grounded;
		game->wheel_direction = car->steer_angle;

		if (python->reset)
		{
			game_state->reset = true;
			using namespace std::chrono_literals;
			std::this_thread::sleep_for(100ms);
			car = reinterpret_cast<jelly_drift::car*>(game_controller->current_car->mono_object->game_object->real_object->object);
			continue;
		}

		car->throttle = python->throttle;
		car->steering = python->steering;
		car->braking = python->braking;
	}
}

BOOL WINAPI DllMain(HINSTANCE dll_instance, DWORD reason, LPVOID reserved)
{
	if (reason == DLL_PROCESS_ATTACH)
		std::thread(start).detach();

	return TRUE;
}