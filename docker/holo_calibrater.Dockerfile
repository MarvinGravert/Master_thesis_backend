FROM base_master_thesis:latest

COPY Hololens_Vive_Calibrater/modules modules
COPY Hololens_Vive_Calibrater/config config
COPY Hololens_Vive_Calibrater/utils utils
COPY Hololens_Vive_Calibrater/main.py .

CMD [ "python","-u","main.py" ]