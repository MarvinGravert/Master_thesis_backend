# Backend servicer

This program acts as the information distributor (mainly in regards to lighthouse information) for entire backend infrastructure. It offers interfaces for the Lighthouse service to push data regarding the tracked objects as well as information retrieval RPC concering those objects to other services. Furthermore, it keeps track of the status and the calibration of the system. 

## Interfaces

### gRPC

* LighthouseReport: client stream-unary gRPC Server: Accepts a new state for all the currently tracked Lighthouse objects and stores them in "VR-objects" which are updated whenever new information is received
* GetTrackerState: unary-unary gRPC-Server: Returns the current pose of the trackers in the system (holo and calibration tracker)
* UpdateCalibration: unary-unary gRPC-Server: Accepts a new calibration and incorperates it into the information provision  
* ChangeStatus: unary-unary gRPC-Server: accepts a new status string which is integrated into the tcp/IP interface

### Tcp/IP

* Acquire controller position+systemstate: This is supposed to be used by the hololens. Initially (aka pre-calibration) the raw values from the Lighthouse are submitted. After calibration has been updated (at least once), it is incorperated into the pose calculation and send to the hololens. For more information see the documentation of the holo-vive calibrator or the quick notes further down below.

As a side note: the status that is transmitted is used in the hololens to debug/change internal values to facilitate testing as changing-recompiling-uploading to the hololens takes multiple minutes and thus is a major hurdle while prototyping

## Calibration 

The calibration is incoporated after information regarding it is received via the UpdateCalibration interface. Beforehand the lighthouse data is forwarded directly. Afterwards the calibration is used as follows:

1. General information: The received calibration concerns the transformation between the virtual center of projection and tracker mounted on the side of the hololens. It is of interest to inform the hololens about the controller pose in relation to virtual center of projection
2. We have available the pose of the controller and the tracker on the side of the hololens in Lighthosue coordinates
3. The line of desired transformation is as follows: controller(inLH)->inverted(tracker)->inverted(calibration)
4. This transform from the controller space to the virtual projection space 

