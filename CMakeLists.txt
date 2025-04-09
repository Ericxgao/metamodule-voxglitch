cmake_minimum_required(VERSION 3.24)

if(NOT "${METAMODULE_SDK_DIR}" STREQUAL "")
	message("METAMODULE_SDK_DIR set by CMake variable ${METAMODULE_SDK_DIR}")
elseif (DEFINED ENV{METAMODULE_SDK_DIR})
    set(METAMODULE_SDK_DIR "$ENV{METAMODULE_SDK_DIR}")
	message("METAMODULE_SDK_DIR set by environment variable ${METAMODULE_SDK_DIR}")
else()
    set(METAMODULE_SDK_DIR "${CMAKE_CURRENT_LIST_DIR}/../metamodule-plugin-sdk")
	message("METAMODULE_SDK_DIR set to default: ${METAMODULE_SDK_DIR}")
endif()
include(${METAMODULE_SDK_DIR}/plugin.cmake)

project(VoxGlitch VERSION 2.32.4 DESCRIPTION "VoxGlitch for Rack" LANGUAGES C CXX)

# Set C++17 standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Add option for virtual build
option(BUILD_VIRTUAL "Build for virtual environment" ON)

# Define source directories
set(SOURCE_DIR ${CMAKE_CURRENT_SOURCE_DIR}/voxglitch)

# Main library target
add_library(VoxGlitch STATIC)

# Compiler definitions
target_compile_definitions(VoxGlitch PRIVATE 
    __V1x 
    __PLUGIN
    $<$<BOOL:${BUILD_VIRTUAL}>:BUILD_VIRTUAL>
    _MB_CAPABLE=1
)

# Compiler options
target_compile_options(VoxGlitch PRIVATE
    -fpermissive
    -fdata-sections
    -ffunction-sections
    -fno-exceptions
    -fno-threadsafe-statics
    -fno-use-cxa-atexit
    $<$<CXX_COMPILER_ID:GNU>:-fvisibility=hidden>
    $<$<CXX_COMPILER_ID:GNU>:-fvisibility-inlines-hidden>
)

# Linker options
target_link_options(VoxGlitch PRIVATE
    -Wl,--gc-sections
)

# Source files
file(GLOB_RECURSE VOXGLITCH_SOURCES
    ${SOURCE_DIR}/src/plugin.cpp
    ${SOURCE_DIR}/src/autobreak.cpp
)

# Explicitly add the main ByteBeat.cpp file but none of the others
target_sources(VoxGlitch PRIVATE
    ${VOXGLITCH_SOURCES}
    ${SOURCE_DIR}/src/ByteBeat.cpp
)

# Include directories
target_include_directories(VoxGlitch PRIVATE 
    ${SOURCE_DIR}/src
    ${SOURCE_DIR}/src/Autobreak
    ${SOURCE_DIR}/src/ByteBeat
)

# Create the plugin
create_plugin(
    SOURCE_LIB      VoxGlitch
    PLUGIN_NAME     VoxGlitch
    PLUGIN_JSON     ${SOURCE_DIR}/plugin.json
    SOURCE_ASSETS   ${CMAKE_CURRENT_LIST_DIR}/assets
    DESTINATION     ${CMAKE_CURRENT_LIST_DIR}/metamodule-plugins
) 