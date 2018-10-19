# WebControl

A web-based version of [MaslowCNC/GroundControl](https://www.github.com/MaslowCNC/GroundControl)

## Developing

### Virtualenv

You can use virtualenv to set up a local development environment for running the code without installing packages in the system Python installation.

    # Create a virtual environment
    virtualenv -p python3 .venv 
    # Activate the virtual environment
    source .venv/bin/activate
    # Install the prerequisites
    pip install -r requirements.txt

Then you can run the code with.

    python main.py

The server will then be available at http://localhost:5000

### Docker

You can build a Docker image with

    docker build -t madgrizzle/webcontrol .

Then you can run it directly

    docker run -it -p 5000:5000 --privileged madgrizzle/webcontrol

Or push it up to Docker Hub

    docker push madgrizzle/webcontrol

Note that the image can only be run from the same architecture it was built from. For example, an image built on an x86 laptop cannot be run on a RaspberryPi.

### Automatic code formatting

This project uses [black](https://github.com/ambv/black) to automatically format python code. To run the autoformatter, simply install black locally with `pip`.

    pip install black

Subsequently, you can just run `black .` to format all files in the current directory. 

    black .

### IDE

[Pycharm Community Edition](https://www.jetbrains.com/pycharm/download) is a free, well-featured Python IDE.

With the [File Watchers](https://plugins.jetbrains.com/plugin/7177-file-watchers) and [BlackPycharm](https://plugins.jetbrains.com/plugin/10563-black-pycharm) plugins you can set up your editor to automatically format your code on save. Then you never have to think about code formatting again :tada:

![PyCharm Screenshot](https://user-images.githubusercontent.com/218876/47197011-817e1600-d318-11e8-8172-eb2c1ffe2d21.png)
