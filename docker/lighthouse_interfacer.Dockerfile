FROM base_master_thesis:latest

COPY Lighthouse_Interfacer/modules modules
COPY Lighthouse_Interfacer/utils utils
COPY Lighthouse_Interfacer/config config
COPY Lighthouse_Interfacer/main.py .

CMD [ "python","-u","main.py" ]