CMAKE_MINIMUM_REQUIRED(VERSION 3.0.2 FATAL_ERROR)

PROJECT(extract-locations VERSION 0.0.1 LANGUAGES C CXX)

IF(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
  SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14 -Wall -Wextra -pedantic -Wold-style-cast -Wuninitialized -Wunreachable-code -Wstrict-overflow=3 -D_FORTIFY_SOURCE=2 -ffunction-sections -fdata-sections")
  SET(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,-O1 -Wl,--hash-style=gnu -Wl,--sort-common -Wl,--gc-sections")

  IF(${CMAKE_CXX_COMPILER_ID} MATCHES "GNU")
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fmax-errors=1")
    IF (${CMAKE_BUILD_TYPE} MATCHES "Debug")
      SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Og -ggdb3 -fno-omit-frame-pointer")
    ENDIF()
  ELSEIF(${CMAKE_CXX_COMPILER_ID} MATCHES "Clang")
    SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -ferror-limit=1")
    IF (${CMAKE_BUILD_TYPE} MATCHES "Debug")
      SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fno-omit-frame-pointer")
    ENDIF()
  ENDIF()
ELSE()
  MESSAGE(FATAL_ERROR "Unsupported system. Feel free to add flags for your system to CMakeLists.txt")
ENDIF()

FIND_PACKAGE(Threads REQUIRED)

FIND_PACKAGE(Boost 1.59.0 REQUIRED)
ADD_DEFINITIONS(-DBOOST_ALL_DYN_LINK)

LIST(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/third_party/libosmium/cmake")
SET(OSMIUM_INCLUDE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/third_party/libosmium/include")
FIND_PACKAGE(Osmium REQUIRED COMPONENTS pbf)

ADD_EXECUTABLE(${PROJECT_NAME} ${PROJECT_NAME}.cc)
TARGET_INCLUDE_DIRECTORIES(${PROJECT_NAME} SYSTEM PUBLIC ${Boost_INCLUDE_DIRS} ${OSMIUM_INCLUDE_DIRS})
TARGET_LINK_LIBRARIES(${PROJECT_NAME} ${Boost_LIBRARIES} ${CMAKE_THREAD_LIBS_INIT} ${OSMIUM_LIBRARIES})
