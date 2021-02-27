FROM base_point_registration

COPY modules modules
COPY client.py .

CMD [ "python","-u","client.py" ]
