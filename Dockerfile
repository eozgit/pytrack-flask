FROM python:3

RUN apt-get clean && \
    apt-get update && \
    apt-get dist-upgrade -y && \
    apt-get install -y vim && \
    apt-get install -y curl

COPY ./* /usr/src/app/
WORKDIR /usr/src/app/

RUN pip install -r requirements.txt
