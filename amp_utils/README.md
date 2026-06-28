# Utils

---

This repository contains all files and folders not designed for a proper function or simply not organized yet. They are here for probable future use.

# ROS Interfaces

> [!WARNING]
> The interfaces which are presented here are not organized and therefore are not related. This implies for the user to add the description to a new package or folder added in this repository.

## Topics (Example)

- self.track_sub = Subscriber(self,TrackStamped,"track")
- self.pointcloud_pub = Publisher(self,PointCloud2,"pointcloud")

> Topics and messages used in Utils package.

---

| Module | Direction | Topic         | Message Type              | Notes             |
| ------ | --------- | ------------- | ------------------------- | ----------------- |
| Utils  | Sub       | `/track`      | `nav_msgs/TrackStamped`   | Track input       |
| Utils  | Pub       | `/pointcloud` | `sensor_msgs/PointCloud2` | Pointcloud output |

# Dependencies

Core dependencies (minimum):

- ROS 2 Humble (or newer)
- `rclcpp` / `rclpy`
- `nav_msgs`, `sensor_msgs`, `fs_msgs`
- `ament_cmake`
- `colcon` (build system)

# Folders descriptions

## Camera Utils

This **folder** is designed for storing **camera-related codes**. Now, there are two Python files developed also for calculations involving camera errors.

## Pointcloud RGB Launcher

This **launcher** is designed for launching the pointcloud

## Rosbag Converter

This **"package"** is designed for converting **track** rosbags to **CSV** files.


# Workspace Lockfile 
Files responsible for cloning all the correct versions of each package that integrates this pipeline.
Using workspace.lock.repos, it is possible to freeze functional versions of the code by recording the exact and immutable versions of all dependencies used to build an artifact, ensuring that anyone can reproduce the same build result.

After executing the given commands in the terminal, a workspace.lock.repos file will be generated in the workspace root directory. Move this file to the pipeline_releases directory and give it a name that reflects the functionality of that version
## Commands 
### Creating the lockfile 
 ```bash
cd ~/ros2_ws
vcs export --exact src > workspace.lock.repos
   ```
> [!NOTE]
> - Scans all Git repositories inside the src/ directory
> - Reads the exact commit hash currently checked out in each repository
> - Writes a `.repos` file containing the repository URLs and their immutable commit versions
> - Creates a reproducible snapshot of the entire pipeline
### Moving file to correct place
 ```bash
mv workspace.lock.repos pipeline_releases/
   ```
> [!NOTE]
> - Moves the generated lockfile to the directory reserved for pipeline releases
> - Keeps release artifacts separated from development files
### Renaming file 
 ```bash
mv pipeline_releases/workspace.lock.repos pipeline_releases/amp_pipeline_humble_2026-01-14.lock.repos
   ```
> [!NOTE]
> - Rename the lockfile to reflect the pipeline version
> - Makes it clear which functionality, ROS distribution, and validation date this pipeline version corresponds to
## Using a frozen pipeline version
 ```bash
vcs import src < pipeline_releases/amp_pipeline_humble_2026-01-14.lock.repos
colcon build
   ```
> [!NOTE]
> - Clones all repositories listed in the lockfile
> - Rebuilds the same pipeline that was previously validated


