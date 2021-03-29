FROM base_master_thesis:latest

COPY waypoint_manager/modules modules
COPY waypoint_manager/config config
COPY waypoint_manager/utils utils
COPY waypoint_manager/server.py .

CMD [ "python","-u","server.py" ]

# docker-compose