FROM resin/raspberrypi3-alpine-python:latest
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt

CMD ["redis-server"]



#FROM python:3.4-alpine