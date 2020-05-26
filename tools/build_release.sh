#!/bin/bash
VARIANT=$1

# cleanup
rm -rf dist

# Build the bundles
pyinstaller --noconfirm main-onedir.spec
pyinstaller --noconfirm main.spec

# Rename the directory
pushd dist

# Zip the releases
touch webcontrol-"${VARIANT}"-singledirectory.tar.gz
pushd main
tar -zcvf ../webcontrol-"${VARIANT}"-singledirectory.tar.gz .
popd
touch webcontrol-"${VARIANT}"-singlefile.tar.gz
tar -zcvf webcontrol-"${VARIANT}"-singlefile.tar.gz webcontrol
ls -l

popd

