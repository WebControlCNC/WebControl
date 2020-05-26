#!/bin/bash

mkdir -p dist/
touch dist/webcontrol-universal.tar.gz

tar -zcvf dist/webcontrol-universal.tar.gz --exclude=dist --exclude=.venv --exclude=.git .

