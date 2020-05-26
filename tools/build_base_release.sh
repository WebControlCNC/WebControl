#!/bin/bash

mkdir -p dist/webcontrol
touch dist/webcontrol/webcontrol-base.tar.gz

tar -zcvf dist/webcontrol/webcontrol-base.tar.gz --exclude=dist --exclude=.venv --exclude=.git .

