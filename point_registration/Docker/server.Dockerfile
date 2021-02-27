FROM base_point_registration

COPY modules modules
COPY server.py .

CMD [ "python","-u","server.py" ]

# docker-compose 