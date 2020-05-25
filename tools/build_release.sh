#!/bin/bash
VARIANT=$1

# Build the one-dir bundle
pyinstaller --noconfirm main-onedir.spec

# Rename the directory
pushd dist
mv main webcontrol
pushd webcontrol

# Zip the directory
touch webcontrol-"${VARIANT}"-singledirectory.tar.gz
tar -zcvf webcontrol-"${VARIANT}"-singledirectory.tar.gz --exclude=webcontrol-"${VARIANT}"-singledirectory.tar.gz .
ls -l

popd
popd

