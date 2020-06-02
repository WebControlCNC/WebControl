#!/bin/bash

# n.b., this implementation of sed flags is for Linux and is not portable to Unix/Mac OS machines.
find docs -type f -exec sed -i "s|https://raw.githubusercontent.com/WebControlCNC/WebControl/master/docs/||g" {} \;