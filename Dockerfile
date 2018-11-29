FROM arm32v7/python:3.5.6-slim-stretch as builder

# Install dependencies needed for building and running OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
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
# TODO: Maybe we can cache wheel files outside this container, for more granular reuse when requiremnts.txt changes
RUN pip install -r /requirements.txt

# Download and compile the Arduino firmware
# Generates the firmware as /firmware/.pioenvs/megaatmega2560/firmware.hex
# PlatformIO doesn't support python3 yet, so also install python2 :/
# See also: https://github.com/platformio/platformio-core/issues/895
RUN apt-get update \
    && apt-get install -y --no-install-recommends python2.7 python-pip python-setuptools python-wheel git \
    && pip2 install -U platformio \
    && pio platform install --with-package framework-arduinoavr atmelavr

ARG madgrizzle_firmware_repo=https://github.com/madgrizzle/Firmware.git
ARG madgrizzle_firmware_sha=bf4350ffd9bc154832505fc0125abd2c4c04dba7
RUN git clone $madgrizzle_firmware_repo firmware/madgrizzle \
    && cd firmware/madgrizzle \
    && git checkout $madgrizzle_firmware_sha \
    && pio run -e megaatmega2560 \
    && mkdir build \
    && mv .pioenvs/megaatmega2560/firmware.hex build/$madgrizzle_firmware_sha-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex
ARG maslowcnc_firmware_repo=https://github.com/MaslowCNC/Firmware.git
ARG maslowcnc_firmware_sha=d0943e2a2f29faef4c07585a00638d0f822e5daf
RUN git clone $maslowcnc_firmware_repo firmware/maslowcnc \
    && cd firmware/maslowcnc \
    && git checkout $maslowcnc_firmware_sha \
    && pio run -e megaatmega2560 \
    && mkdir build \
    && mv .pioenvs/megaatmega2560/firmware.hex build/$maslowcnc_firmware_sha-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex

ADD . /WebControl
# Clean up the /WebControl dir a bit to slim it down
# TODO: Is there a more automatic way to do this?
RUN rm -rf /WebControl/.venv && rm -rf /WebControl/.git
# Pre-compile the pyc files (for faster Docker image startup)
RUN python --version && python -m compileall /WebControl


FROM arm32v7/python:3.5.6-slim-stretch

# Pip wheels compiled in the builder
COPY --from=builder /root/.cache /root/.cache
# requirements.txt with opencv and numpy removed
COPY --from=builder /requirements.txt /requirements.txt
# Required shared libraries
COPY --from=builder /usr/local/lib/python3.5/site-packages/cv2.cpython-35m-arm-linux-gnueabihf.so /usr/local/lib/python3.5/site-packages/cv2.cpython-35m-arm-linux-gnueabihf.so
COPY --from=builder /usr/lib/libf77blas.so /usr/lib/libf77blas.so
COPY --from=builder /usr/lib/libf77blas.so.3 /usr/lib/libf77blas.so.3
COPY --from=builder /usr/lib/libcblas.so.3 /usr/lib/libcblas.so.3
COPY --from=builder /usr/lib/libatlas.so.3 /usr/lib/libatlas.so.3
COPY --from=builder /usr/lib/libblas.so.3 /usr/lib/libblas.so.3
COPY --from=builder /usr/lib/arm-linux-gnueabihf/libgfortran.so.3 /usr/lib/arm-linux-gnueabihf/libgfortran.so.3
COPY --from=builder /usr/lib/liblapack.so.3 /usr/lib/liblapack.so.3

RUN pip install numpy && pip install -r /requirements.txt && rm -rf /root/.cache

# Install avrdude
# TODO: to speed up incremental docker builds, we can probably do this in the builder image if we can figure out
# which files we need to copy over
RUN apt-get update && apt-get install -y --no-install-recommends \
    avrdude \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get -y autoremove
# Copy in the pre-compiled firmware
COPY --from=builder /firmware/madgrizzle/build/* /firmware/madgrizzle/
COPY --from=builder /firmware/maslowcnc/build/* /firmware/maslowcnc/

# Copy the pre-compiled source from the builder
COPY --from=builder /WebControl /WebControl

WORKDIR /WebControl
EXPOSE 5000/tcp
CMD python /WebControl/main.py
