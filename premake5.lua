workspace "jelly_drift_interface"
configurations { "Debug", "Release" }

project "jelly_drift_interface"
    kind "SharedLib"
    language "C++"
    targetdir "bin/%{cfg.buildcfg}"
    architecture "x64"
    characterset "MBCS"

    files {
        "gym_jd/interface/cpp/**.hpp",
        "gym_jd/interface/cpp/**.cpp",
    }

    cppdialect "c++latest"

    buildoptions { "/MP" } -- Multi processor compilation

    filter "configurations:Debug"
        defines { "DEBUG" }
        symbols "On"

    filter "configurations:Release"
        defines { "NDEBUG" }
        optimize "Speed"
        buildoptions { "/Ot" } -- Favour speed
