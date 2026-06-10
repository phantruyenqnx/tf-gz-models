cmake_minimum_required(VERSION 3.22)
project(gtec_uwb_gz_harmonic)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE RelWithDebInfo)
endif()

find_package(gz-cmake3 REQUIRED)
find_package(gz-sim8 REQUIRED)
find_package(gz-transport13 REQUIRED)
find_package(gz-msgs10 REQUIRED)
find_package(gz-math7 REQUIRED)
find_package(gz-plugin2 REQUIRED COMPONENTS register)

enable_testing()
find_package(GTest)

gz_msgs_generate_messages(
  TARGET gtec_msgs
  PROTO_PACKAGE "gtec_msgs.msgs"
  MSGS_PATH "${CMAKE_CURRENT_SOURCE_DIR}/proto"
  MSGS_PROTOS "${CMAKE_CURRENT_SOURCE_DIR}/proto/gtec_msgs/msgs/ranging.proto"
  DEPENDENCIES gz-msgs10::gz-msgs10
)

if(GTest_FOUND)
  add_executable(Ranging_TEST test/Ranging_TEST.cc)
  target_link_libraries(Ranging_TEST GTest::gtest_main ${PROJECT_NAME}-gtec_msgs)
  add_test(NAME Ranging_TEST COMMAND Ranging_TEST)
endif()

add_library(uwb_core STATIC
  src/UwbChannelModel.cc
  src/UwbChannelModel_tables.cc)
target_include_directories(uwb_core PUBLIC include)
target_link_libraries(uwb_core PUBLIC gz-math7::gz-math7)

if(GTest_FOUND)
  add_executable(UwbChannelModel_TEST test/UwbChannelModel_TEST.cc)
  target_link_libraries(UwbChannelModel_TEST GTest::gtest_main uwb_core)
  add_test(NAME UwbChannelModel_TEST COMMAND UwbChannelModel_TEST)
endif()

# Temporary object so the project configures before real sources exist.
add_library(placeholder OBJECT src/placeholder.cc)
