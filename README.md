# EventDriveFSM

This repository contains the core packages responsible for managing the autonomous software pipeline of the **Ampera Racing** autonomous vehicle.

## Packages

### `amp_utils`

`amp_utils` contains a collection of utility nodes and shared tools used across the autonomous system.

Its main purpose is to provide reusable components that support the rest of the software stack, such as communication helpers, debugging tools, and other general utilities.

---

### `amp_sm`

`amp_sm` is the package responsible for the vehicle's **Finite State Machine (FSM)**.

It controls the vehicle's operating states and handles the transitions between them based on events received from the autonomous system. The state machine is implemented using **SMACC2** and coordinates the overall behavior of the vehicle during operation.

---

## Repository Structure

```text
EventDriveFSM/
├── amp_sm/        # Vehicle finite state machine
└── amp_utils/     # Shared utilities and helper nodes
```

## Purpose

The goal of this repository is to provide the software components that coordinate the behavior of the autonomous vehicle while offering the shared utilities required by the rest of the system.
