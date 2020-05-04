FROM ubuntu:latest
MAINTAINER Alexey Fillipov
RUN apt-get update -y
RUN apt-get update -y \
  && apt-get install -y python3-pip python3-dev \
  && pip3 install --upgrade pip
COPY . /parser
WORKDIR /parser
RUN pip3 install -r requirements.txt
CMD [ "python3", "./app.py" ]
