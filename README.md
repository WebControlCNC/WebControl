# WebControl

WebControl is a browser-based implementation of Ground Control (see https://github.com/MaslowCNC/GroundControl) for controlling a Maslow CNC.  Ground Control utilizes Kivy as the graphic front end, which makes it difficult to implement multiple and/or remote access.  WebControl, however, runs completely as a flask-socketio web server and inherently supports remote access and multiple screens.  Therefore, WebControl can be installed on a low cost device like a Raspberry Pi and the user can utilize their laptop, tablet and/or phone to control it.. all at the same time.  Since the the installation supports headless operation, someone trying to build a self contained sled (i.e., motors located on the sled) can also install the Raspberry Pi on the sled as well.

## Getting Started

These instructions are based upon using a Raspberry Pi (RPi) for running WebControl.  WebControl should be able to be run on any computer capable of running Python 3.  The instructions also assume a headless operation of the RPi and that it configured with an IP address and SSH capability.

### Prerequisites

What things you need to install the software and how to install them

```
Maslow CNC
Raspberry Pi configured for Internet access and SSH capability
```

### Installing Docker onto Raspberry Pi

WebControl can be installed by two different methods; either by downloading from github or from downloading the docker.  Unless you are intending to perform development work on WebControl, we strongly recommend downloading the docker.  Because of some of the libraries that are used for optical calibration, it can take hours to install from source.

Log into your RPi via SSH and issue these commands:
```
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
sudo groupadd docker
sudo gpasswd -a $USER docker
newgrp docker
```
These commands will download and install docker and create a docker group that allows you to run docker without using sudo.

Test the installation of docker by issuing the following command:

```
docker run hello-world
```

### Installing WebMCP docker onto Raspberry Pi

There are two ways to run WebControl.  The first downloading and running the webcontrol docker and the second is by downloading and running WebMCP docker.  WebMCP is "supervisor" program that can be used to start, stop and upgrade WebControl.  The advantage if using WebMCP is that it provides a means to monitor and control WebControl from a browser.  If WebControl seems non-responsive or something is amiss (it is still alpha-software), you can use WebMCP to see its health and stop/restart WebControl if needed.  We have documentation (TBD) that describes how to start WebMCP upon boot of the RPi.  Once configured, you won't need to SSH into the RPi to start/stop webcontrol.

While logged into the RPi, issue the following command:
```
docker pull madgrizzle/webmcp
docker run -it -v $HOME/.WebControl:/root/.WebControl -v /var/run/docker.sock:/var/run/docker.sock -p 5001:5001 -e HOST_HOME=$HOME --network=“host” --privileged madgrizzle/webmcp
```

You can put the long "docker run" command into a script and run the script instead of typing it in ##add content about doing all this upon boot#

### Setting Up WebMCP to Run on Boot

Added to the TODO List

### Not Using WebMCP But Want To Run WebControl?

So, if you don't want to use WebMCP, you can issue the following command to download the webcontrol docker and run it:

```
docker pull madgrizzle/webcontrol
docker run -it -v $HOME/.WebControl:/root/.WebControl -p 5000:5000 --privileged madgrizzle/webcontrol python main.py
```

### How to Download from Github and Run WebControl

This is on the TODO list

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

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

Added to TODO list?

## Authors

* **Madgrizzle** - *Initial work* - [madgrizzle](https://github.com/madgrizzle)
* **John Boiles** - *Docker Expert* - [johnboiles](https://github.com/johnboiles)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

TBD..

