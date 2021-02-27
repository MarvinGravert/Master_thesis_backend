# Point Matching Module

This module acts as a server which accepts 3D point pairs (maybe 2D later) and produces a mapping between the points sets. Input data is assumed to be passed in in pairs. The point correspondance problemthus already solved

## API

The api is implemnted using grpc.

### Client->Server

* **pointSet_1**: array of (x,y,z) points of point set 1
* **pointSet_2**: array of (x,y,z) points of points set 2
* **algorithm**: Definings the type of algorith, whether result is optimized and the ransac parameters. See below for more details

### Server->Client

* **status**: string success or not: => string due to it beign easier to extend
* **rotationMatrix**: repeated list of float. Row major rotation matrix
* **translationVector**: repeated float

### Algorithm config

The config is passed as an grpc object though the  client offers a function to create this configuration via a dictionary:

* **type**: Type of Algorithm [str]
* **optimize**: optimize y/n [bool]
* **ransac**: Threshold, confidence List[float,float]

## Algorithms

So far two are implemented:

* **Kabsch**: Find the R, t using linear optimization
* **OpenCV**: Find the (affine transformation) R,t using optimization as well as Ransac

## Optimization

If the "optimize" field in the algorithm is set to True, a nonlinear least squared
optimization is run on the result.

## Usage

Use the docker-compose or start the server.py from the main directory.

