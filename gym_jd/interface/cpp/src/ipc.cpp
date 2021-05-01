#include "ipc.hpp"
#include <windows.h>
#include <string>

HANDLE ipc::python_mutex = NULL, ipc::game_mutex = NULL;
ipc::message_python* ipc::python_buffer = NULL;
ipc::message_game* ipc::game_buffer = NULL;

bool ipc::initialize()
{
	HANDLE map_python, map_game;
	// Get the names of the files
	std::string name_python = "Local\\jd_python_" + std::to_string(GetCurrentProcessId());
	std::string name_game = "Local\\jd_game_" + std::to_string(GetCurrentProcessId());
	std::string name_python_mutex = "Local\\jd_python_mutex_" + std::to_string(GetCurrentProcessId());
	std::string name_game_mutex = "Local\\jd_game_mutex_" + std::to_string(GetCurrentProcessId());

	// Open the file mappings
	if ((map_python = OpenFileMappingA(FILE_MAP_READ, FALSE, name_python.c_str())) == NULL)
		return false;

	if ((map_game = OpenFileMappingA(FILE_MAP_WRITE, FALSE, name_game.c_str())) == NULL)
		return false;
	
	// Map views of the files
	if ((python_buffer = reinterpret_cast<ipc::message_python*>(MapViewOfFile(map_python, FILE_MAP_READ, 0, 0, sizeof(message_python)))) == NULL)
	{
		CloseHandle(map_python);
		return false;
	}
	CloseHandle(map_python);

	if ((game_buffer = reinterpret_cast<ipc::message_game*>(MapViewOfFile(map_game, FILE_MAP_WRITE, 0, 0, sizeof(message_game)))) == NULL)
	{
		CloseHandle(map_game);
		return false;
	}
	CloseHandle(map_game);

	if ((ipc::python_mutex = OpenMutexA(MUTEX_ALL_ACCESS, FALSE, name_python_mutex.c_str())) == NULL)
	{
		return false;
	}

	if ((ipc::game_mutex = OpenMutexA(MUTEX_ALL_ACCESS, FALSE, name_game_mutex.c_str())) == NULL)
	{
		CloseHandle(ipc::python_mutex);
		return false;
	}

	return true;
}