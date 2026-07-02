# Autonomous State Machine (SMACC2 Integration)

## Overview

This branch introduces the new event-driven autonomous state machine built on top of the SMACC2 library. The objective is to replace imperative state management with a strictly orthogonal, reactive architecture that dictates the vehicle's operational phases, ensuring deterministic transitions based on CAN telemetry and lifecycle node callbacks.

## State Machine Architecture

The system is built around `amp_sm` and operates through a defined set of states and events triggered by internal logic or external CAN signals (via `fs_msgs`).

### Implemented States

* **st_AsOff:** Default idle state.
* **st_AsChecking:** Executes steering and actuator calibration routines.
* **st_AsCalibration:** Planned state. It will be responsible for executing real-time sensor calibration prior to arming the vehicle.
* **st_AsReady:** Vehicle is armed and awaiting the GO signal for the selected mission (e.g., Skidpad, Trackdrive).
* **st_AsDriving:** Active lateral and longitudinal control.
* **st_AsFinished:** Mission complete, safe shutdown sequence triggered.

### Implemented Events

State transitions are primarily handled by specific listeners:

* `EvCheckListener`
* `EvCalibrationListener`
* `EvMissionSelectListener`
* `EvFinishedListener`

## System Dependencies

Building this branch requires specific ROS 2 (Humble) packages, particularly for SMACC2's internal state tracing capabilities.

Ensure the tracing tools are installed in your environment to prevent `ld` (linker) errors related to `TRACETOOLS_TRACEPOINT`:

```bash
sudo apt-get update
sudo apt-get install lttng-tools liblttng-ust-dev ros-humble-tracetools

```

Required custom packages (must be present in the workspace):

* `fs_msgs`
* `lifecycle_msgs`

## Build Instructions

To compile the state machine and its associated lifecycle nodes, it is recommended to clean the build cache first to avoid stale CMake configurations, especially if swapping branches.

```bash
cd ~/ws
rm -rf build/amp_sm install/amp_sm
colcon build --packages-select amp_sm --symlink-install
source install/setup.bash

```

## Launching

To run the state machine node:

```bash
ros2 launch amp_sm amp_sm.launch.py

```

## Development Notes & TODOs

* **Tracing:** LTTng tracing is currently active for SMACC2 state transitions. Monitor the overhead during Trackdrive missions.
* **Lifecycle Integration:** `check_lifecycle_node.cpp` is linked, but transitions between `Unconfigured` and `Active` need strict synchronization with `st_AsChecking`.
* **Memory Leaks:** Verify `ISmaccOrthogonal` cleanup during `st_AsFinished` to ensure no dangling pointers remain before process termination.
