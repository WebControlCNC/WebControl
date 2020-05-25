#!/bin/bash
mkdir -p firmware
pushd firmware

# Download the latest release
curl -s https://api.github.com/repos/webcontrolcnc/Firmware/releases/latest \
  | grep "browser_download_url.*hex" \
  | cut -d : -f 2,3 \
  | tr -d \" \
  | wget -qi -

mkdir -p maslowcnc
mv maslowcnc*.hex maslowcnc/

mkdir -p holey
mv holey*.hex holey/

mkdir -p madgrizzle
mv madgrizzle*.hex madgrizzle/

popd
