FROM resin/raspberrypi3-alpine-python:latest
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
