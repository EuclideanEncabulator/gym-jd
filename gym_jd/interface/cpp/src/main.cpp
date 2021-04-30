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

	//jelly_drift::car* car = objects::find_active_object<jelly_drift::car>("FD8(Clone)");
	auto game_controller = objects::find_active_object<jelly_drift::game_controller>("GameController");
	
	//std::string scene = "Menu";
	//objects::load_scene(scene);
	//while (true)
	//{
	//	using namespace std::chrono_literals;
	//	objects::set_time_scale(10.0f);
	//	std::this_thread::sleep_for(5ms);
	//	objects::set_time_scale(0.0f);
	//	std::this_thread::sleep_for(20ms);
	//}

	auto car = reinterpret_cast<jelly_drift::car*>(game_controller->current_car->mono_object->game_object->real_object->object);

	std::cout << game_controller->current_car << std::endl;
	std::cout << car << std::endl;

	while (true)
	{
		unity::vector3 position = objects::get_position(car->centre_of_mass);
		std::cout << "pos: " << position.x << " " << position.y << " " << position.z << std::endl;
		unity::quaternion rotation = objects::get_rotation(car->centre_of_mass);
		std::cout << "rot: " << rotation.w << " " << rotation.x << " " << rotation.y << " " << rotation.z << std::endl;
		car->throttle = 1.0f;
		car->steering = 0.0f;
		car->braking = false;
	}
}

BOOL WINAPI DllMain(HINSTANCE dll_instance, DWORD reason, LPVOID reserved)
{
	if (reason == DLL_PROCESS_ATTACH)
		std::thread(start).detach();

	return TRUE;
}