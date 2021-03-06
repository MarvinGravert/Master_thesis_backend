# Master Thesis

## Modules

Note the **hololens** module is in its own repo

* **backend_servicer**: This service acts as the information accumulator/distributor for everything involing the lighthouse tracked objects. This means that it acts the sole service the lighthouse servicer provides information to, where as other services such as hololens-vive-calibrator or the hololens inquire about the state from this service
* **lighthouse servicer**: Service polls the OpenVR interface, packages the received information and sends it to the information and sends it to the backend_servicer
* **hololens**: the hololens is the user facing programs that allows: calibration, calibration evaluation and waypoint placing 
* **hololens-vive-calibrator**: Calculate the transformation (aka the calibration) between the lighthouse KOS and the hololens KOS
* **waypoint manager**: Accepts new waypoints from the hololens and using the avaiable information (tracker position+calibration information) to display the desired position in lighthouse coordinates
* **status manager**: Allows to set a status for the system which can be used to control the data flow in the hololens
* **points registering**: Service used to calculate the transformation between two point sets
  
## TODOs

* Config Querying: Implement UpdateCalibration and GetCalibration Workflows
* Multi User Config Management on Hololens
* Config File/config persistance 
* ROS Integration
* continous server side streaming of controller state
* way point manager
* robot calibration manager (manually)