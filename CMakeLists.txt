#----------------------------------------------------------------------------
# Setup the project
cmake_minimum_required(VERSION 3.16...3.21)
project(Brachy)

#----------------------------------------------------------------------------
# Find Geant4 package, activating all available Vis drivers by default
# You can set WITH_GEANT4_VIS to OFF via the command line or ccmake/cmake-gui
# to build a batch mode only executable
#
option(WITH_GEANT4_UIVIS "Build example with Geant4 UI and Vis drivers" ON)
if(WITH_GEANT4_UIVIS)
  find_package(Geant4 REQUIRED ui_all vis_all)
else()
  find_package(Geant4 REQUIRED)
endif()
#----------------------------------------------------------------------------
# Setup Geant4 include directories and compile definitions
#
include(${Geant4_USE_FILE})
#----------------------------------------------------------------------------
# Locate sources and headers for this project
#
include_directories(${PROJECT_SOURCE_DIR}/include
                     ${Geant4_INCLUDE_DIR} )

#----------------------------------------------------------------------------

file(GLOB sources ${PROJECT_SOURCE_DIR}/src/*.cc)
file(GLOB headers ${PROJECT_SOURCE_DIR}/include/*.hh)

#----------------------------------------------------------------------------
# Add the executable, and link it to the Geant4 libraries
#
add_executable(Brachy Brachy.cc ${sources} ${headers})

target_link_libraries(Brachy ${Geant4_LIBRARIES})

#----------------------------------------------------------------------------
# Copy all scripts to the build directory, i.e. the directory in which we
# build basic_brachy. This is so that we can run the executable directly because it
# relies on these scripts being in the current working directory.
#

set(brachy_SCRIPTS
   macros/IodineSourceMacro.mac  macros/LeipzigSourceMacro.mac macros/VisualisationMacro.mac
   analysis/macro.C macros/iridium_source_primary.mac macros/iodine_source_primary.mac macros/iridium_source_leipzig_primary.mac
   analysis/plot_primary.C  macros/iodine_decay.mac macros/FlexiSourceMacro.mac
   macros/TG186SourceMacro.mac macros/TG186_iridium_decay.mac macros/OncuraIodineSourceMacro.mac
  )

foreach(_script ${brachy_SCRIPTS})
  get_filename_component(_script_name ${_script} NAME)
  configure_file(
    ${PROJECT_SOURCE_DIR}/${_script}
    ${PROJECT_BINARY_DIR}/${_script_name}
    COPYONLY
    )
endforeach()

#----------------------------------------------------------------------------
# Install the executable to 'bin' directory under CMAKE_INSTALL_PREFIX
#
install(TARGETS Brachy DESTINATION bin)

