FROM arm32v7/python:3.5.6-slim-stretch

# Install dependencies needed for building and running OpenCV
RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    # to build and install
    unzip wget sed \
    build-essential cmake pkg-config \
    # to work with images (likely not necessary for optical calibration)
    # libjpeg-dev libtiff-dev libpng-dev \
    # to work with video / webcam (likely not necessary for optical calibration)
    # libavcodec-dev libavformat-dev libswscale-dev \
    libv4l-dev \
    # for opencv math operations
    libatlas-base-dev gfortran \
    # thread building blocks (not availabe on the arm version of python:3.5.6-slim-stretch)
    # libtbb2 libtbb-dev \
    # for gevent
    libevent-dev \
    # for numpy (installs libf77blas.so.3)
    libatlas-base-dev \
    # cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove

# OpenCV dependency
RUN pip install numpy

# Build OpenCV
ADD tools/download_build_install_opencv.sh /download_build_install_opencv.sh
RUN chmod +x /download_build_install_opencv.sh && /download_build_install_opencv.sh

# Get other python dependencies
ADD requirements.txt /requirements.txt
# Remove opencv and numpy from requirements (since they're already installed)
RUN sed -i '/opencv-python.*/d' /requirements.txt && sed -i '/numpy.*/d' /requirements.txt
RUN pip install -r /requirements.txt 

# Remove no-longer-needed gevent compilation libraries
RUN apt-get purge -y --auto-remove --allow-remove-essential gcc libevent-dev wget unzip sed

# Copy the source
ADD . /WebControl

WORKDIR /WebControl
EXPOSE 5000/tcp
CMD python /WebControl/main.py
