FROM base_master_thesis:latest

COPY point_registration/modules modules
COPY point_registration/config config
COPY point_registration/utils utils
COPY point_registration/server.py .

# CMD [ "sleep","10" ] 

CMD [ "python","-u","server.py" ]

# docker-compose