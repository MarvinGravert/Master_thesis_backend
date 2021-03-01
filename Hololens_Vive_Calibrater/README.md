# Holo Vive Calibrator

This repo is tasked with receiving the virtual position of the hololens calibration object via a tcp/ip connection. Afterwards it inquires about the position of the trackers (tracker on the hololens and tracker on the calibration object). The position of the virtual object and the postion of the tracker are thrown into a points calculator module which returns a number of points. These are matches together via points registration and finally the postion of the holo tracker relative to the virtual center of projection is calculated.

## Architecture

There are multiple modules that are dedicated to one operation:

* Async GRPC client to get data from the tracker via the backend server
* Async TCP/IP server to receive data from hololens 
* Async gRPC client to communicate with points registration server
* Transformation module that manages applying the transformation
* Point_correcpsondance, which finds the points of interest in the 3D object