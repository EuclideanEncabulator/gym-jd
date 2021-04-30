workspace "jelly_drift_ppo"
configurations { "Debug", "Release" }

project "jelly_drift_ppo"
    kind "SharedLib"
    language "C++"
    targetdir "bin/%{cfg.buildcfg}"
    architecture "x64"
    characterset "MBCS"

    includedirs {
		"dependencies/cppzmq-4.7.1",
        "dependencies/cppzmq-4.7.1/libzmq-4.3.1/include"
	}

    files {
        "src/**.hpp",
        "src/**.cpp",
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