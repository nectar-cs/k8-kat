FROM ubuntu:latest

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

EXPOSE 5000
ADD . /app

WORKDIR /app
RUN pip3 install -r requirements.txt
CMD python3 app.py
