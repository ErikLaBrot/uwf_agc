cmake_minimum_required(VERSION 3.8)
project(agc_golfcart_sim)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(ignition-gazebo6 REQUIRED)
find_package(ignition-plugin1 REQUIRED COMPONENTS register)

# Add include directories explicitly
include_directories(
  /usr/include/ignition/plugin1
  /usr/include/ignition/gazebo6
)

# Build Gazebo plugin directly
add_library(ackermann_steering_plugin SHARED
  plugins/gazebo/ackermann_steering/ackermann_steering_plugin.cpp
)

target_link_libraries(ackermann_steering_plugin
  ignition-gazebo6::ignition-gazebo6
  ignition-plugin1::register
)

set_target_properties(ackermann_steering_plugin PROPERTIES
  CXX_STANDARD 17
  CXX_STANDARD_REQUIRED ON
)

# Install the C++ plugin
install(TARGETS ackermann_steering_plugin
  LIBRARY DESTINATION lib
  ARCHIVE DESTINATION lib
  RUNTIME DESTINATION bin
)

# Install Python modules
ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  ${PROJECT_NAME}/c2000_sim_bridge.py
  DESTINATION lib/${PROJECT_NAME}
)

# Install directories
install(DIRECTORY
  launch
  worlds
  models
  config
  DESTINATION share/${PROJECT_NAME}/
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()