#!/bin/bash
rm -rf build
mkdir build
rm -rf firmware
mkdir firmware
cd firmware
mkdir madgrizzle
mkdir maslowcnc
mkdir holey

cd ../build
madgrizzle_firmware_repo=https://github.com/madgrizzle/Firmware.git
madgrizzle_firmware_sha=bf4350ffd9bc154832505fc0125abd2c4c04dba7
git clone $madgrizzle_firmware_repo firmware/madgrizzle
cd firmware/madgrizzle
git checkout $madgrizzle_firmware_sha
pio run -e megaatmega2560

mv .pio/build/megaatmega2560/firmware.hex ~/WebControl/firmware/madgrizzle/madgrizzle-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex

cd ../..

maslowcnc_firmware_repo=https://github.com/MaslowCNC/Firmware.git
maslowcnc_firmware_sha=e1e0d020fff1f4f7c6b403a26a85a16546b7e15b
git clone $maslowcnc_firmware_repo firmware/maslowcnc
cd firmware/maslowcnc
git checkout $maslowcnc_firmware_sha
pio run -e megaatmega2560
mv .pio/build/megaatmega2560/firmware.hex ~/WebControl/firmware/maslowcnc/maslowcnc-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex

cd ../..

holey_firmware_repo=https://github.com/madgrizzle/Firmware.git
holey_firmware_sha=950fb23396171cbd456c2d4149455cc45f5e6bc3
git clone $holey_firmware_repo firmware/holey
cd firmware/holey
git checkout $holey_firmware_sha
pio run -e megaatmega2560
mv .pio/build/megaatmega2560/firmware.hex ~/WebControl/firmware/holey/holey-$(sed -n -e 's/^.*VERSIONNUMBER //p' cnc_ctrl_v1/Maslow.h).hex
