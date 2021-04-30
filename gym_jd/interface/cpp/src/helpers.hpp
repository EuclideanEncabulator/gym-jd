#pragma once

#include <windows.h>

namespace helpers
{
	bool is_in_module(uintptr_t address, HMODULE module);
	uintptr_t get_module_size(HMODULE module);
	bool is_valid_memory(uintptr_t address);
}