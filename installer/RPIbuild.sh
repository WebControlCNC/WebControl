#!/bin/bash
cd ..
rm -rf build
mkdir build
rm -r firmware
mkdir firmware
cd firmware

mkdir holey
mkdir maslowcnc
cd ..
cp ../Hex/norm.hex ./firmware/maslowcnc/maslowcnc-1.29.hex
cp ../Hex/holey.hex ./firmware/holey/holey-51.30.hex
rm -r dist
mkdir dist
#cd WebControl
pyinstaller ./main-onedir.spec
cd dist/main
mkdir ../releases
mv main webcontrol
#cd ..
#mv main webcontrol
#cd WebControl
touch webcontrol-rpi-singledirectory.tar.gz
tar -zcvf webcontrol-rpi-singledirectory.tar.gz --exclude=webcontrol-rpi-singledirectory.tar.gz .
cp webcontrol-rpi-singledirectory.tar.gz ../releases

cd ~/pybuild
#rm -r dist
#rm -r build
