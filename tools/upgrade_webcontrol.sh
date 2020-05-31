#!/bin/bash
sleep 3
echo $1
echo $2
cd $2
tar -zxvf $1

# Install dependencies if we're running on Raspbian
IS_RASPBIAN=$(cat /etc/os-release | grep "Raspbian")
if [ -n "${IS_RASPBIAN}" ]
then
  echo "We are on Raspbian, installing dependencies"
  sudo tools/install_dependencies.sh
fi

echo "Starting WebControl"
./webcontrol
