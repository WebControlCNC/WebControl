FROM python:3.5.6-slim-stretch

ADD . /WebControl
RUN pip install -r /WebControl/requirements.txt

WORKDIR /WebControl
EXPOSE 5000/tcp
CMD python /WebControl/main.py
