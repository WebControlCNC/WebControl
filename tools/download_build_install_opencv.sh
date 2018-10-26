#!/bin/bash
# Based on https://github.com/mohaseeb/raspberrypi3-opencv-docker

OPENCV_VERSION=3.4.3

WS_DIR=`pwd`
mkdir opencv
cd opencv

# download OpenCV and opencv_contrib
wget -O opencv.zip https://github.com/opencv/opencv/archive/$OPENCV_VERSION.zip
unzip opencv.zip
rm -rf opencv.zip

# TODO: Try with no opencv_contrib (we might not need it for optical calibration)
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/$OPENCV_VERSION.zip
unzip opencv_contrib.zip
rm -rf opencv_contrib.zip

OPENCV_SRC_DIR=`pwd`/opencv-$OPENCV_VERSION
OPENCV_CONTRIB_MODULES_SRC_DIR=`pwd`/opencv_contrib-$OPENCV_VERSION/modules

# build and install
cd $OPENCV_SRC_DIR
mkdir build && cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE \
  -D CMAKE_INSTALL_PREFIX=/usr/local \
  -D OPENCV_EXTRA_MODULES_PATH=$OPENCV_CONTRIB_MODULES_SRC_DIR \
  -D BUILD_SHARED_LIBS=OFF \
  -D ENABLE_NEON=ON \
  -D ENABLE_VFPV3=ON \
  -D BUILD_TESTS=OFF \
  -D INSTALL_PYTHON_EXAMPLES=OFF \
  -D BUILD_EXAMPLES=OFF \
  ..

make -j4

make install
ldconfig

# verify the installation is successful
python3 -c "import cv2; print('Installed OpenCV version is: {} :)'.format(cv2.__version__))"
if [ $? -eq 0 ]; then
    echo "OpenCV installed successfully! ........................."
else
    echo "OpenCV installation failed :( ........................."
    SITE_PACKAGES_DIR=/usr/local/lib/python2.7/site-packages
    echo "$SITE_PACKAGES_DIR contents: "
    echo `ls -ltrh $SITE_PACKAGES_DIR`
    echo "Note: temporary installation dir $WS_DIR/opencv is not removed!"
    exit 1
fi

# cleanup
cd $WS_DIR
rm -rf opencv
