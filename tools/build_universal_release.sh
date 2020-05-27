#!/bin/bash

# create the webcontrol script
touch webcontrol
chmod +x webcontrol
echo "#!/bin/bash" > webcontrol
echo "" >> webcontrol
echo "python3 main.py" >> webcontrol

mkdir -p dist/
touch dist/webcontrol-universal.tar.gz

tar -zcvf dist/webcontrol-universal.tar.gz --exclude=dist --exclude=.venv --exclude=.git .

