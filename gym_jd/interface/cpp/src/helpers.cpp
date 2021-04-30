#include "helpers.hpp"

#include <psapi.h>
#include <windows.h>

bool helpers::is_in_module(uintptr_t address, HMODULE module)
{
    uintptr_t start = reinterpret_cast<uintptr_t>(module);
    uintptr_t end = start + get_module_size(module);

    return address >= start && address <= end;
}

uintptr_t helpers::get_module_size(HMODULE module)
{
    MODULEINFO module_info;
    K32GetModuleInformation(GetCurrentProcess(), module, &module_info, sizeof(MODULEINFO));
    return module_info.SizeOfImage;
}

bool helpers::is_valid_memory(uintptr_t address)
{
    MEMORY_BASIC_INFORMATION memory_info;
    VirtualQuery(reinterpret_cast<LPCVOID>(address), &memory_info, sizeof(MEMORY_BASIC_INFORMATION));

    return memory_info.Protect == PAGE_READWRITE && memory_info.State == MEM_COMMIT && memory_info.Type == MEM_PRIVATE;
}