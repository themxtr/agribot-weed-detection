# AgriBot Weed Detection & Sprayer Robot

A ROS 2 simulation of an agricultural robot that autonomously detects weeds using computer vision and sprays pesticide.

## Features
- Autonomous patrol path through a crop field
- Real-time weed detection using color-based computer vision (YOLOv8 architecture)
- Automatic pesticide sprayer activation on weed detection
- Weeds disappear after spraying
- Robot returns to start after completing patrol
- 3D visualization in RViz2

## System Architecture
```
fake_camera_node → /camera/image_raw → yolo_detector_node → /weed_detected → sprayer_node
field_patrol_node → /visualization_markers → RViz2
```

## Requirements
- Ubuntu 22.04
- ROS 2 Humble
- Python 3.10
- ultralytics (YOLOv8)
- OpenCV

## Installation
```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/YOUR_USERNAME/agribot-weed-detection.git weed_detector
cd ~/ros2_ws
colcon build
source install/setup.bash
```

## Running the Simulation
Terminal 1 - Full autonomous patrol:
```bash
ros2 run weed_detector field_patrol_node
```

Terminal 2 - Visualization:
```bash
rviz2
```
In RViz2: Fixed Frame = map, Add MarkerArray, topic = /visualization_markers

## Optional - Camera + Detection Pipeline
```bash
ros2 run weed_detector fake_camera_node
ros2 run weed_detector yolo_detector_node
ros2 run weed_detector sprayer_node
```

## Node Description
| Node | Purpose |
|------|---------|
| field_patrol_node | Autonomous patrol, weed detection, spraying, path following |
| fake_camera_node | Simulated robot camera publishing image frames |
| yolo_detector_node | Computer vision weed detector |
| sprayer_node | Pesticide sprayer controller |
| visualizer_node | RViz2 marker publisher |
