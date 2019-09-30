#!/bin/bash
sleep 3
echo $1
echo $2
cd $2
tar -zxvf $1
./webcontrol
