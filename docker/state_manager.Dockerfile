FROM base_master_thesis:latest

COPY state_manager/config config
COPY state_manager/main.py .

# CMD [ "python","-u","main.py" ]

# docker-compose