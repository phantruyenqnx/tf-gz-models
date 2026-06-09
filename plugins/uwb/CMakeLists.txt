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

# Temporary object so the project configures before real sources exist.
add_library(placeholder OBJECT src/placeholder.cc)
