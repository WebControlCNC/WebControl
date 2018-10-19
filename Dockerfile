FROM python:3.5.6-slim-stretch

ADD . /WebControl
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libevent-dev python-all-dev\
    && rm -rf /var/lib/apt/lists/* \
    && pip install -r /WebControl/requirements.txt \
    && apt-get purge -y --auto-remove gcc libevent-dev python-all-dev

WORKDIR /WebControl
EXPOSE 5000/tcp
CMD python /WebControl/main.py
