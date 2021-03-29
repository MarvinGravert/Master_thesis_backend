FROM base_master_thesis:latest

COPY backend_servicer/modules modules
COPY backend_servicer/api api
COPY backend_servicer/config config
COPY backend_servicer/server.py .
# CMD [ "sleep","10" ]
CMD [ "python","-u","server.py" ]

# docker-compose