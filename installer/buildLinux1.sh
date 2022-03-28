#!/bin/bash
# in WebControl/installer
cd ..
# move to root folder from installer folder "WebControl"
echo %path%
rm -rf build
mkdir build
rm -rf firmware
mkdir firmware
cd firmware
mkdir maslowcnc
mkdir holey
# in WebControl/firmware folder
cd ..
# in WebControl folder
cp ../Hex/norm.hex ./firmware/maslowcnc/maslowcnc-1.29.hex
cp ../Hex/holey.hex ./firmware/holey/holey-1.30.hex

rm -r dist  #removes the distribution folder
mkdir dist
#This makes the single folder distribution
#make the distribution but only with Webcontrol stuff (.WebControl, WCvenv)
pyinstaller ./main-onedir.spec

# WebControl/dist/main/
cd dist/main
#mkdir releases

mkdir ../releases
touch ../releases/webcontrol-linux-singledirectory.tar.gz
tar -zcvf ../releases/webcontrol-linux-singledirectory.tar.gz --exclude=webcontrol-linux-singledirectory.tar.gz .
#mv webcontrol-linux-singledirectory.tar.gz ../releases

# WebControl
cd ../..

#This makes the single file distribution
#rm -r dist
#pyinstaller main.spec
#cd dist
#touch webcontrol-linux-singlefile.tar.gz
#tar -zcvf webcontrol-linux-singlefile.tar.gz --exclude=webcontrol-linux-singlefile.tar.gz .
#mv webcontrol-linux-singlefile.tar.gz ../releases
