#include "ipc.hpp"
#include <windows.h>
#include <string>

HANDLE map_python, map_game;
PVOID python_buffer, game_buffer;

bool ipc::initialize()
{
	// Get the names of the files
	std::string name_python = "Local\\jd_python_" + std::to_string(GetCurrentProcessId());
	std::string name_game = "Local\\jd_game_" + std::to_string(GetCurrentProcessId());

	// Open the file mappings
	if ((map_python = OpenFileMappingA(FILE_MAP_READ, FALSE, name_python.c_str())) == NULL)
		return false;

	if ((map_game = OpenFileMappingA(FILE_MAP_WRITE, FALSE, name_game.c_str())) == NULL)
		return false;
	
	// Map views of the files
	if ((python_buffer = MapViewOfFile(map_python, FILE_MAP_READ, 0, 0, sizeof(message_python))) == NULL)
	{
		CloseHandle(map_python);
		return false;
	}

	if ((game_buffer = MapViewOfFile(map_game, FILE_MAP_WRITE, 0, 0, sizeof(message_game))) == NULL)
	{
		CloseHandle(map_game);
		return false;
	}

	return true;
}

ipc::message_game* ipc::game()
{
	return reinterpret_cast<ipc::message_game*>(game_buffer);
}

ipc::message_python* ipc::python()
{
	return reinterpret_cast<ipc::message_python*>(python_buffer);
}