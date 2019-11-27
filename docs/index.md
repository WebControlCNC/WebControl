---
layout: default
title: Home
nav_order: 1
description: Help pages for WebControl
wcversion: 0.915.001
---

# WebControl

On Github: [madgrizzle/WebControl](https://github.com/madgrizzle/WebControl)

Report Issues: [madgrizzle/WebControl/issues](https://github.com/madgrizzle/WebControl/issues)

WebControl is a browser-based implementation of [MaslowCNC/GroundControl](https://github.com/MaslowCNC/GroundControl) for controlling a Maslow CNC.  Ground Control utilizes Kivy as the graphic front end, which makes it difficult to implement multiple and/or remote access.  WebControl, however, runs completely as a flask-socketio web server and inherently supports remote access and multiple screens.  Therefore, WebControl can be installed on a low cost device like a Raspberry Pi, Windows 10, or linux (Debian) machines and the user can utilize their laptop, tablet and/or phone to control it.. all at the same time.  Since the the installation supports headless operation, someone trying to build a self contained sled (i.e., motors located on the sled) can also install the Raspberry Pi on the sled as well.

<img src="assets/Screenshot.png" alt="Screenshot" width="100%">
## Notice

Webcontrol will be moving all releases to a pyinstaller created executable, including for the Raspberry Pi.  I will try to create a pre-built image for the RPI, but until then you will need to install a copy of raspbian on an SD card, update it for SSH and network access, then download webcontrol and set it to run automatically (if you chose).

### Windows 10 and Linux Single-File Releases

For Windows 10 and Linux (Debian-based, such as Ubuntu) machines, users can download the latest single-file release, extract it, and run webcontrol.  As a single-file release, it is completely portable and does not require an installation.  The file unpacks itself into a temporary directory and runs.  If you have a very slow computer, it might take a while to unpack.  In that case, it is recommended to use the single-directory release which extracts into a single directory containing unpacked files.  Startup is much quicker using single-directory releases versus a single-file release.

Check out the release page at:

[https://github.com/madgrizzle/WebControl/releases](https://github.com/madgrizzle/WebControl/releases)

### Raspberry Pi (3B+ & Zero W)

For Raspberry Pi's, single-directory releases are your best option.  It can take up to a minute to unpack a single-file release on a Raspberry Pi 3B+.  Single-directory releases unpack the files into the directory so startup is much quicker.  Both the Raspberry Pi 3B+ and Zero W have been tested to work with webcontrol.  Other versions likely would also.  I recommend the 3B+ if you are trying to decide.

Check out the release page at:

[https://github.com/madgrizzle/WebControl/releases](https://github.com/madgrizzle/WebControl/releases)

## Built With

* [Flask](http://flask.pocoo.org/) - The web framework used
* [Flask-Socketio](https://github.com/miguelgrinberg/Flask-SocketIO) - Websocket integration for communications with browser clients
* [Bootstrap4](https://getbootstrap.com/) - Front-end component library
* [Jinja2](http://jinja.pocoo.org/) - Template engine for web page generation
* [Feather.js](https://feathersjs.com/) - Only icon library I could find that had diagonal arrows.. works well to boot.
* [OpenCV](https://github.com/skvark/opencv-python) - Library for computer vision to implement optical calibration
* [Numpy](http://www.numpy.org) - Library for math routines used with optical calibration
* [Scipy](http://www.scipy.org) - Another library for math routines used with optical calibration
* [Imutils](https://github.com/jrosebr1/imutils) - Adrian Rosebrock's library used with optical calibration
* [Schedule](https://github.com/dbader/schedule) - Library used to schedule checking connection with arduino
* [Ground Control](https://github.com/maslowcnc/groundcontrol) - Much of this was adapted from the Kivy-based Ground Control


## Developing

### Virtualenv

You can use virtualenv to set up a local development environment for running the code without installing packages in the system Python installation.

    # Create a virtual environment
    virtualenv -p python3 .venv 
    # Activate the virtual environment
    source .venv/bin/activate
    # Install the prerequisites
    pip install -r requirements.txt

When running on the Pi, you'll also need some extra dependencies and will need to build OpenCV from source. See the Dockerfile for details. (TODO: add instructions here)

Then you can run the code with.

    python main.py

The server will then be available at http://localhost:5000

### Automatic code formatting

This project uses [black](https://github.com/ambv/black) to automatically format python code. To run the autoformatter, simply install black locally with `pip`.

    pip install black

Subsequently, you can just run `black .` to format all files in the current directory. 

    black .

If you don't have python3.6+ locally (to be able to run `black`), you can run `black` in a Docker container.

    docker run -v $(pwd):/code johnboiles/python-black .

### IDE

[Pycharm Community Edition](https://www.jetbrains.com/pycharm/download) is a free, well-featured Python IDE.

With the [File Watchers](https://plugins.jetbrains.com/plugin/7177-file-watchers) and [BlackPycharm](https://plugins.jetbrains.com/plugin/10563-black-pycharm) plugins you can set up your editor to automatically format your code on save. Then you never have to think about code formatting again :tada:

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

Added to TODO list?

## Authors

* **Madgrizzle** - *Initial work* - [madgrizzle](https://github.com/madgrizzle)
* **John Boiles** - *Docker Expert* - [johnboiles](https://github.com/johnboiles)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

See [LICENSE](https://github.com/madgrizzle/WebControl/blob/master/LICENSE)
