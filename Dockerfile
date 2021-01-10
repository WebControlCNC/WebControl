FROM debian:buster-slim

# Install dependencies needed for building and running OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip python3-setuptools python3-dev \
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
    avrdude libffi-dev libxml2-dev libxslt-dev \
    libsm6 libxext6 libxrender-dev git \
    # Install requirements that don't play well with armv7+rpi via pip
    python3-opencv python3-scipy python3-numpy \
    # cleanup
    && apt-get -y autoremove \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Get other python dependencies
ADD requirements.txt /requirements.txt
# Remove opencv, scipy and numpy from requirements (since they're already installed)
RUN sed -i '/opencv-python.*/d' /requirements.txt && sed -i '/scipy.*/d' /requirements.txt && sed -i '/numpy.*/d' /requirements.txt
RUN pip3 install -r /requirements.txt

# Download and compile the Arduino firmware
# Generates the firmware as /firmware/.pioenvs/megaatmega2560/firmware.hex
# Python3 support was added in July, 2019: https://github.com/Homebrew/homebrew-core/pull/41821
RUN apt-get update \
    && pip3 install -U platformio \
    && pio platform install --with-package framework-arduino atmelavr \
    && pio lib -g install "Servo"

ARG madgrizzle_firmware_repo=https://github.com/madgrizzle/Firmware.git
ARG madgrizzle_firmware_sha=bf4350ffd9bc154832505fc0125abd2c4c04dba7
RUN git clone $madgrizzle_firmware_repo firmware/madgrizzle \
    && cd firmware/madgrizzle \
    && git checkout $madgrizzle_firmware_sha \
    && pio run -e megaatmega2560 \
    && mkdir build \
    && mv .pio/build/megaatmega2560/firmware.hex build/$madgrizzle_firmware_sha-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex
ARG maslowcnc_firmware_repo=https://github.com/MaslowCNC/Firmware.git
ARG maslowcnc_firmware_sha=e1e0d020fff1f4f7c6b403a26a85a16546b7e15b
RUN git clone $maslowcnc_firmware_repo firmware/maslowcnc \
    && cd firmware/maslowcnc \
    && git checkout $maslowcnc_firmware_sha \
    && pio run -e megaatmega2560 \
    && mkdir build \
    && mv .pio/build/megaatmega2560/firmware.hex build/$maslowcnc_firmware_sha-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex
RUN pwd
ARG  holey_firmware_repo=https://github.com/madgrizzle/Firmware.git
ARG  holey_firmware_sha=950fb23396171cbd456c2d4149455cc45f5e6bc3
RUN git clone $holey_firmware_repo firmware/holey \
    && cd firmware/holey \
    && git checkout $holey_firmware_sha \
    && pio run -e megaatmega2560 \
    && mkdir build \
    && mv .pio/build/megaatmega2560/firmware.hex build/$holey_firmware_sha-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex

ADD . /WebControl

# Pre-compile the pyc files (for faster Docker image startup)
RUN python3 -m compileall /WebControl

WORKDIR /WebControl
EXPOSE 5000/tcp
CMD python3 /WebControl/main.py
