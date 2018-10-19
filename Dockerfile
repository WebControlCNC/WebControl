FROM python:3.5.6-slim-stretch

# Get prerequisites for compiling gevent
RUN apt-get update \
&& apt-get install -y --no-install-recommends gcc libevent-dev python-all-dev \
&& rm -rf /var/lib/apt/lists/* 

# Get python dependencies
ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt 

# Remove no-longer-needed gevent compilation libraries
RUN apt-get purge -y --auto-remove gcc libevent-dev python-all-dev

# Copy the source
ADD . /WebControl

WORKDIR /WebControl
EXPOSE 5000/tcp
CMD python /WebControl/main.py
