# Holo Vive Calibrator

This repo is groupin all funcionatliy surrounding the calibration between the virtual and real world (as in the LH world). This includes managing the calculation and distribution of the calibration besides accepting calibration information form the Hololens.

There are essentially four workflows:

1. Accept new calibration data from Hololens via TCP/IP. Start calculation process to arrive at a new calibration. Update all services that depend on that information and write information into a file
2. Upon request provide with hololens with a list of all calibration files currently stored #TOBEDONE
3. Upon request from the hololens update all other services who depend on this information (way point calculator and backend servicer) about this #TOBEDONE
4. Provide services who inquire about it, about the current calibration in use #TOBEDONE

## Workflow 1: Calibration

The program implements the consumer/producer pattern. The incoming messages of the

1. Start the Async Communiation server who wait for a connection of hololens with calibration information
2. After receiving information, send put the information into a queue
3. A worker will take a job from the queue
4. Initially a gRPC request to the backend_servicer for the tracker position will be started (as smallest delay as possible!)
5. The message will be put into a parser who decides on the further workflow (as of now only one exist)
6. The received transformation will be used to calculate the virtual calibration points 
7. The calibration trackers position will be used to calculate teh real calibration points
8. Both point sets are transmitted to the point registering service
9. The received transformation is used to calculate the transformation between virtual center of hololens and the attached tracker on the hololens
10. (All Services are updated about the new calibration)
11. Calibration is written to a file

## Architecture

There are multiple modules that are dedicated to one operation:

* Async GRPC client to get data from the tracker via the backend server
* Async TCP/IP server to receive data from hololens 
* Async gRPC client to communicate with points registration server
* Transformation module that manages applying the transformation
* Point_correcpsondance, which finds the points of interest in the 3D object