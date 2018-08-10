FROM resin/raspberrypi3-alpine-python:3.4
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
