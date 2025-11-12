cmake_minimum_required(VERSION 3.10)
project(ackermann_steering_plugin)

# Find Gazebo
find_package(gazebo REQUIRED)
find_package(ignition-gazebo6 REQUIRED)

# Include directories
include_directories(${GAZEBO_INCLUDE_DIRS})
link_directories(${GAZEBO_LIBRARY_DIRS})

# Build the plugin
add_library(ackermann_steering_plugin SHARED ackermann_steering_plugin.cpp)
target_link_libraries(ackermann_steering_plugin ${GAZEBO_LIBRARIES})

# Set C++ standard
set_target_properties(ackermann_steering_plugin PROPERTIES
  CXX_STANDARD 17
  CXX_STANDARD_REQUIRED ON
)

# Install
install(TARGETS ackermann_steering_plugin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  RUNTIME DESTINATION bin
)