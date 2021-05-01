#include "objects.hpp"
#include "offsets.hpp"
#include "unity.hpp"
#include "helpers.hpp"

#include <windows.h>
#include <psapi.h>
#include <iostream>

uintptr_t gameobjectmanager, unityplayer_base, unityplayer_size;

bool objects::initialize()
{
    HMODULE unityplayer_handle = GetModuleHandleA("UnityPlayer.dll");

    if (unityplayer_handle == NULL)
        return false;

    unityplayer_base = reinterpret_cast<uintptr_t>(unityplayer_handle);
	gameobjectmanager = *reinterpret_cast<uintptr_t*>(unityplayer_base + offsets::gameobjectmanager);

	return true;
}

uintptr_t objects::find_object(std::string name, uintptr_t offset, uint32_t limit)
{
    unity::object* current_object = reinterpret_cast<unity::object*>(gameobjectmanager + offset);
    unity::mono_object* first_object = NULL;

    for (unsigned int i = 0; i < limit; i++)
    {
        current_object = current_object->next_object;

        unity::mono_object* mono_object = current_object->mono_object;

        if (mono_object == NULL)
            break;

        if (!helpers::is_valid_memory(reinterpret_cast<uintptr_t>(mono_object)))
            continue;

        if (!helpers::is_valid_memory(reinterpret_cast<uintptr_t>(*mono_object->name)))
            continue;

        if (first_object == mono_object)
            break;
        else if (first_object == NULL)
            first_object = mono_object;

        if (name.compare(*mono_object->name) == 0)
        {
            return reinterpret_cast<uintptr_t>(current_object->mono_object->game_object->real_object->object);
        }
    }

    return NULL;
}

unity::vector3 objects::get_position(uintptr_t transform)
{
    unity::vector3 position;

    static const auto get_position_Injected = reinterpret_cast<uint64_t(__fastcall*)(uintptr_t, unity::vector3&)>(unityplayer_base + offsets::get_position_Injected);
    get_position_Injected(transform, position);

    return position;
}

unity::quaternion objects::get_rotation(uintptr_t transform)
{
    unity::quaternion rotation;

    static const auto get_rotation_Injected = reinterpret_cast<uint64_t(__fastcall*)(uintptr_t, unity::quaternion&)>(unityplayer_base + offsets::get_rotation_Injected);
    get_rotation_Injected(transform, rotation);

    return rotation;
}

bool objects::set_time_scale(float time_scale)
{
    static const auto set_time_scale = reinterpret_cast<uint64_t(__fastcall*)(float time_scale)>(unityplayer_base + offsets::set_time_scale);
    set_time_scale(time_scale);
    return true;
}