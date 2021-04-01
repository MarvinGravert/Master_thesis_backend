# Robot-Vive Manual Calibration module
This module is used to:
1. retrieve the pose of the endeffector mounted tracker
2. Calculate the transformation between LH and robot given a list of correspondances of points in the robot base frame (null frame) and tracker poses

Originally this was supposed to be an automatic calibration procedure utilising the capabailites of ROS but time constraints have made this infeasible.

## Architecture

The two main functionalites outlined above are realised by two scripts that can be started independently (and probably consecutively).

- **poll_calibration_pose**
- **register_robot_LH**

### poll_calibration_points

This relies on the `triad_openvr.py` module to repeatedly query the pose of the tracker. This pose is written into a file which is uniquely created via checkign preexisting files and 


### Other modules

`triad_openvr` and `linear_algebra_helper.py`