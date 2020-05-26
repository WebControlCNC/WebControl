#!/bin/bash

apt-get update

apt-get install -y --no-install-recommends python3-pip python3-setuptools python3-dev unzip wget sed build-essential cmake pkg-config libv4l-dev libatlas-base-dev gfortran libevent-dev libatlas-base-dev avrdude libffi-dev libxml2-dev libxslt-dev libsm6 libxext6 libxrender-dev git python3-opencv python3-scipy python3-numpy libjasper1 libgstreamer1.0-0 libavcodec58 libqtgui4 libqt4-test

apt-get -y autoremove

# Remove opencv, scipy and numpy from requirements (since they're already installed)
sed -i '/opencv-python.*/d' requirements.txt
sed -i '/scipy.*/d' requirements.txt
sed -i '/numpy.*/d' requirements.txt

pip3 install -r requirements.txt
