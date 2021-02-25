# Lighthouse Interfacer

This module interfaces with the lighthouse and thus with the tracked objects. It reports their data via GRPC to the backend_servicer.

The SteamVR interface is polled on a certain frequency (set in the env/config) and the data is processed and streamed to the backed_servicer. Thus, the main purpose of this module is the data processing as well as allowing to run the backend_servicer on a different server than this module (as communication can happen via network)

## Architecture

The client starts and etablishes a connection with the backend_servicer, as well as with the SteamVR interface, afterwards it starts streaming the data to the backend


## Notes

It keeps track of the tracked VR objects and name tags them, it creates a list of 

## GRPC interface

message type for Tracker and Controller. Name, button, Position etc. are updated therein

the button state is submitted via a dict

Its client stream-unary server
