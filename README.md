---
layout: default
title: Home
nav_order: 1
description: Help pages for WebControl
wcversion: 0.915.001
tags: web-control
---
# WebControl

The official tool for [Maslow CNC](https://www.maslowcnc.com/); control your Maslow with any web browser.

* Browser-based, multi-platform controller software.
* Connects to Maslow's Arduino Mega (or similar) via USB.
* Includes setup instructions (updated from [Maslow Community Garden](http://maslowcommunitygarden.org/)).
* Runs gcode (`.nc` files) for printing cuts.

You can [report issues](https://github.com/WebControlCNC/WebControl/issues) to the [volunteer team](https://github.com/WebControlCNC/WebControl/).


## Context

WebControl started as a browser-based port of the original GroundControl application, but has grown to support more features:

* The calibration and setup process is better documented and easier to use.
* It implements a flask+socketio web server, so other computers on the network may control the machine.
* It can be run on a low-cost device, like a Raspberry Pi.
* It can also support multiple custom firmwares developed by the community which enhance the Maslow.

At this point, WebControl has become the **de-facto beginner's tool for Maslow**.

<img src="docs/assets/Screenshot.png" alt="Screenshot" width="100%">

## Installation

### Pre-Built Raspberry Pi Image

See the [dedicated repository](https://github.com/WebControlCNC/webcontrol-pi).

### Raspberry Pi
_Replace the version number with the latest release..._

```
cd ~
mkdir webcontrol
cd webcontrol
wget https://github.com/WebControlCNC/WebControl/releases/download/v0.920/webcontrol-0.920-rpi-singledirectory.tar.gz
tar -zxvf webcontrol-0.920-rpi-singledirectory.tar.gz
```

### Linux (Debian)
_Replace the version number with the latest release..._

```
cd ~</br>
mkdir webcontrol
cd webcontrol
wget https://github.com/WebControlCNC/WebControl/releases/download/v0.920/webcontrol-0.920-linux-singledirectory.tar.gz
tar -zxvf webcontrol-0.920-linux-singledirectory.tar.gz
```

### Linux Autostart (systemd)

To run WebControl automatically on startup for a Linux-based machine, it is recommended to create a service:

>nano webcontrol.service

type the following:

>[Unit]</br>
>Description=WebControl</br>
>After=network.target</br>
></br>
>[Service]</br>
>ExecStart=/home/pi/webcontrol/webcontrol</br>
>WorkingDirectory=/home/pi/webcontrol</br>
>StandardOutput=inherit</br>
>StandardError=inherit</br>
>Restart=always</br>
>User=pi</br>
></br>
>[Install]</br>
>WantedBy=multi-user.target</br>

Save file using Ctrl-X/Yes

>sudo cp webcontrol.service /etc/systemd/system

Test with the following:

>sudo systemctl start webcontrol.service

Try to reach webcontrol using your browser.

To debug, try:

>sudo systemctl status webcontrol

Or, to. get logs:

>journalctl -xe

When it works, then type:

>sudo systemctl enable webcontrol.service

see for more details:
https://www.raspberrypi.org/documentation/linux/usage/systemd.md

### Docker & Kubernetes

* Pull the docker image from `inzania/web-control` using the `armv7` or `amd64` tag.
* Mount a data/config volume at `/root/.WebControl`
* Expose port `5000`
* Run with `privileged: true` security context for USB access.

### Remote Access

WebControl can be run behind a front-proxy with TLS termination, such as nginx. You can use this in conjunction with semi-static IP to access your Maslow from anywhere with internet access. The full scope of this is outside this documentation, so you should be sure you understand the **security implications** before proceeding (hint: WebControl doesn't have a login or user authentication system).

## Usage

Open your web browser to `localhost:5000` (or use the IP address of your device).

## Built With

* [Flask](http://flask.pocoo.org/) - The web framework used
* [Flask-Socketio](https://github.com/miguelgrinberg/Flask-SocketIO) - Websocket integration for communications with browser clients
* [Bootstrap4](https://getbootstrap.com/) - Front-end component library
* [Jinja2](http://jinja.pocoo.org/) - Template engine for web page generation
* [Feather.js](https://feathericons.com/) - Only icon library I could find that had diagonal arrows.. works well to boot.
* [OpenCV](https://github.com/skvark/opencv-python) - Library for computer vision to implement optical calibration
* [Numpy](http://www.numpy.org) - Library for math routines used with optical calibration
* [Scipy](http://www.scipy.org) - Another library for math routines used with optical calibration
* [Imutils](https://github.com/jrosebr1/imutils) - Adrian Rosebrock's library used with optical calibration
* [Schedule](https://github.com/dbader/schedule) - Library used to schedule checking connection with arduino
* [Ground Control](https://github.com/maslowcnc/groundcontrol) - Much of this was adapted from the Kivy-based Ground Control


## Developing

### Python Virtual Environment

There are several ways to set up a Python virtual environment (sometimes shown as 'virtualenv' or just 'venv'). Python itself can do this with the command `python -m venv venv` to create a virtual environment called `venv`. However, it's quite common to work with multiple versions of Python itself, so having a tool that can manage multiple Python versions and virtual environments is really helpful.

To manage multiple python versions and virtual environments get `pyenv` (or [`pyenv-win`](https://github.com/pyenv-win/pyenv-win) for Windows)

Here's a well-written [walkthrough](https://community.cisco.com/t5/developer-general-knowledge-base/pyenv-for-managing-python-versions-and-environments/ta-p/4696819) of setting up your system (macOS, Ubuntu/Debian, Fedora/CentOS/RHEL, Windows) for `pyenv` and then using `pyenv` to set up your virtual environment.

Once you've prepared your system and installed `pyenv`
- get the latest version of Python that we know works with WebControl, currently that's `3.10.5`:
    `pyenv install 3.10.5`
- create a virtual environment with it:
    `pyenv virtualenv 3.10.5 webcontrol_3_10`
    The `webcontrol_3_10` name is arbitrary
- activate the virtual environment - this will help isolate what you do from the rest of your system:
    `pyenv activate webcontrol_3_10`

#### Prepare the Virtual Environment itself

This next stuff should only need to be done once in your virtual environment.
- install some useful tools
    `pip install setuptools`
    `pip install pip-tools`
    `pip install black`
- rebuild the list of requirements needed by WebControl (optional)
    You should do this step if you're using a different version of Python from 3.10.5 shown above
    `rm requirements.txt`
    `pip-compile -r requirements.in --resolver=backtracking --verbose`
- install the requirements
    `pip install -r requirements.txt`

And that's the virtual environment creation and set up done. From now on you'll only need to activate the virtual environment after any restart to get going.

#### Virtualenv on a Raspberry Pi

When running on the Pi, you'll also need some extra dependencies and will need to build OpenCV from source. See the Dockerfile for details. (TODO: add instructions here)

### Get the Client Side Libraries Set Up

We're using `npm` (Node Package Manager) to manage the third party JavaScript libraries in use for the client side code (the stuff that actually runs in your browser), `npm` comes with `node`.

Note that we're not using `node` as the web server, we're only using it for `npm` to manage the JavaScript libraries.

To manage `node` it is better to use a node version manager, such as [nvm](https://github.com/nvm-sh/nvm) (or [nvm-windows](https://github.com/coreybutler/nvm-windows) for windows).

Once `nvm` is installed. Run `nvm install lts` to install the latest 'long term support' version of `node`. Which will get you both `node` and `npm`. There are other `nvm` commands, such as `nvm current` to show which version of `node` you're currently using, and `nvm use lts` to switch `nvm` to using the latest `lts` version of `node` if it was on another version.

Then finally go to the `static` folder in the WebControl project, which is where all the Javascript lives, and run `npm install` to get it to download all of the required JavaScript packages. It will create a folder called `node_modules` and put them all within that.

### Now What? Let's Start Up WebControl🎉

Then you can run the code with.

    python main.py

The server will then be available at `http://localhost:5000`

* If you get an error message with something like `ModuleNotFoundError: No module named '_ctypes'` within it. Then it means that you didn't get your system properly prepared before creating your virtual environment (looking at you Ubuntu). Please follow the walkthrough linked above to:
1. deactivate your virtual environment,
2. delete it,
3. prepare your system,
4. recreate your virtual environment.

### Automatic code formatting

This project uses [black](https://github.com/ambv/black) to automatically format python code. To run the autoformatter, simply install black locally with `pip`.

    pip install black

Subsequently, you can just run `black .` to format all files in the current directory.

    black .

If you don't have python3.6+ locally (to be able to run `black`), you can run `black` in a Docker container.

    docker run -v $(pwd):/code johnboiles/python-black .

### IDE

#### PyCharm
[Pycharm Community Edition](https://www.jetbrains.com/pycharm/download) is a free, well-featured Python IDE.

With the [File Watchers](https://plugins.jetbrains.com/plugin/7177-file-watchers) and [BlackPycharm](https://plugins.jetbrains.com/plugin/10563-black-pycharm) plugins you can set up your editor to automatically format your code on save. Then you never have to think about code formatting again :tada:

#### VSCode
[Visual Studio Code](https://code.visualstudio.com/Download) is a free IDE with awesome support for Python (and every other language you can think of). And yes, you can install it on a Raspberry Pi.

Once it picks up that you're working with Python it will advise on extensions that are available to help you get the best out of it, including Python, PyLance, Black, ... Plus built-in support for GitHub, extensions for Docker, Linux under Windows (WSL), and so much more

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

Added to TODO list?

## With Thanks

* **Madgrizzle** - *Initial work* - [madgrizzle](https://github.com/madgrizzle)
* **John Boiles** - *Docker Expert* - [johnboiles](https://github.com/johnboiles)
* **Tinker** - *UI Improvements/Bug Fixer/Etc.* - [gb0101010101](https://github.com/gb0101010101)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

See [LICENSE](https://github.com/WebControlCNC/WebControl/blob/master/LICENSE)
