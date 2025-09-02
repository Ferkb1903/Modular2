# CMakeLists.txt for HDR Brachytherapy Monte Carlo Simulation
cmake_minimum_required(VERSION 3.16...3.21)

# Project name and version
project(HDR_Brachytherapy VERSION 1.0.0)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(Geant4 REQUIRED ui_all vis_all)

# Include Geant4 use file
include(${Geant4_USE_FILE})

# Include directories
include_directories(${PROJECT_SOURCE_DIR}/include)

# Source files
file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB headers ${PROJECT_SOURCE_DIR}/include/*.hh)

# Add executable
add_executable(hdr_brachy main.cc ${sources} ${headers})

# Link to Geant4 libraries
target_link_libraries(hdr_brachy ${Geant4_LIBRARIES})

# Copy macro files to build directory
set(HDR_BRACHY_SCRIPTS
    macros/init_vis.mac
    macros/run_tg43.mac
    macros/run_heterogeneous.mac
    macros/vis.mac
)

foreach(_script ${HDR_BRACHY_SCRIPTS})
    configure_file(
        ${PROJECT_SOURCE_DIR}/${_script}
        ${PROJECT_BINARY_DIR}/${_script}
        COPYONLY
    )
endforeach()

# Install the executable to 'bin' directory under CMAKE_INSTALL_PREFIX
install(TARGETS hdr_brachy DESTINATION bin)

# Create output directories
file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/output)
file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/output/dose_maps)
file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/output/dvh)
file(MAKE_DIRECTORY ${PROJECT_BINARY_DIR}/output/tg43_validation)
