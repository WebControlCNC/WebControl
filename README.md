# WebControl

WebControl is a browser-based implementation of [MaslowCNC/GroundControl](https://github.com/MaslowCNC/GroundControl) for controlling a Maslow CNC.  Ground Control utilizes Kivy as the graphic front end, which makes it difficult to implement multiple and/or remote access.  WebControl, however, runs completely as a flask-socketio web server and inherently supports remote access and multiple screens.  Therefore, WebControl can be installed on a low cost device like a Raspberry Pi, Windows 10, or linux (Debian) machines and the user can utilize their laptop, tablet and/or phone to control it.. all at the same time.  Since the the installation supports headless operation, someone trying to build a self contained sled (i.e., motors located on the sled) can also install the Raspberry Pi on the sled as well.

![Screenshot](https://user-images.githubusercontent.com/218876/47197523-ac1d9e00-d31b-11e8-93c8-93a84a7eb0cf.png)

## Notice

I'm having serious issues with building the docker files.  Unless I can overcome those issues, there won't be any more docker updates.  Therefore, I'm updating this section to put the pyinstall version usage up front...

## Getting Started for Raspberry PI (Recommended Pyinstaller Release Instructions)

For Windows 10 and Linux (Debian-based, such as Ubuntu) machines, users can download the latest single-file release, extract it, and run webcontrol.  As a single-file release, it is completely portable and does not require an installation.  The file unpacks itself into a temporary directory and runs.  If you have a very slow computer, it might take a while to unpack.  In that case, it is recommended to use the single-directory release which extracts into a single directory containing unpacked files.  Startup is much quicker using single-directory releases versus a single-file release.  For RPI, the single-file release is just way to slow, so I don't build it.

**Note, for linux/RPI users, it will extract directly into the directory you are currently in.**  

For Linux/RPI users, make a new subdirectory,and then issue the untar:

**For RPI:**
>cd ~</br>
>mkdir webcontrol</br>
>cd webcontrol</br>
>wget https://github.com/madgrizzle/WebControl/releases/download/v0.920/webcontrol-0.920-rpi-singledirectory.tar.gz</br>
>tar -zxvf webcontrol-0.920-rpi-singledirectory.tar.gz</br>

**For Linux:**
>cd ~</br>
>mkdir webcontrol</br>
>cd webcontrol</br>
>wget https://github.com/madgrizzle/WebControl/releases/download/v0.920/webcontrol-0.920-linux-singledirectory.tar.gz</br>
>tar -zxvf webcontrol-0.920-linux-singledirectory.tar.gz</br>

Change 0.920 to the lastest release if you want.

For Windows users, just extract the zip file as is.

Check out the release page at:

https://github.com/madgrizzle/WebControl/releases


## Getting WebControl to Run Upon Startup on RPI (## NOT FULLY VETTED ##)

Here's tentative instructions on how to get webcontrol to run on startup (from kayaker37 on forum).. This assumes you extracted webcontrol into a subdirectory called webcontrol:

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

Try to reach webcontrol using your browser and if it works, then type:

>sudo systemctl enable webcontrol.service

see for more details:
https://www.raspberrypi.org/documentation/linux/usage/systemd.md 

## Getting Started for Raspberry Pi  (Deprecated Docker.. Please do not use)

These instructions are based upon using a Raspberry Pi (RPi) for running WebControl.  WebControl should be able to be run on any computer capable of running Python 3.  

The simplest way to get started is to use the pre-built RPi image that @johnboiles has put together:

https://drive.google.com/file/d/132811KALMXDlxUa9jGZdCv1eB2lz09Ws/view?usp=sharing 2

Download the file and burn it to your SD card.  Add the appropriate ssh & wpa_supplicant.conf files for your network and then boot it.  It will automatically download the latest WebMCP and start it (takes 3-5 minutes to complete the initial boot process).  WebMCP is a watchdog/control program that allows you to start, stop, and update webcontrol.  It also displays webcontrol messages that would normally print out in the terminal (like groundcontrol would do).  WebMCP is bound to port 5001, so to reach it, open your browser and bring up http://xxx.xxx.xxx.xxx:5001 (where xxx... is your RPI's IP address).

When WebMC comes up, click “Start WebControl” it will download the latest docker image and run it (takes another 3-5 minutes to docwnload).  It may look like nothing is going on for a while, but just let it run.  WebControl is bound to port 5000, so to reach it, browse to http://xxx.xxx.xxx.xxx:5000.

Alternatively, you can install it onto an existing RPI OS by following these instructions.  Note, the instructions assume your RPI has been configured with an IP address and SSH capability.

### Prerequisites

What things you need to install the software and how to install them

* Maslow CNC
* Raspberry Pi configured for Internet access and SSH capability

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
docker run -it -v $HOME/.WebControl:/root/.WebControl -v /var/run/docker.sock:/var/run/docker.sock -p 5001:5001 -e HOST_HOME=$HOME --network=host --privileged madgrizzle/webmcp
```

### Setting Up WebMCP to Run on Boot

You can configure WebMCP to start at boot using the example systemd unit file included in the [WebMCP repo](https://www.github.com/madgrizzle/WebMCP).

```
# TODO this line will eventually pull from madgrizzle/WebMCP directly when that repo is publicly available
sudo curl -fsSL https://gist.githubusercontent.com/johnboiles/da4f3fac73105c82d900e8118dae1ec4/raw/f5bf24641e7ce6c000b5d79dc0c5ed68477566f7/webmcp.service -o /etc/systemd/system/webmcp.service
sudo systemctl start webmcp
sudo systemctl enable webmcp
```

### Not Using WebMCP But Want To Run WebControl?

So, if you don't want to use WebMCP, you can issue the following command to download the webcontrol docker and run it:

```
docker pull madgrizzle/webcontrol
docker run -it -v $HOME/.WebControl:/root/.WebControl -p 5000:5000 --privileged madgrizzle/webcontrol python main.py
```

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

* If you get the following error after trying `python main.py`
    `ImportError: libSM.so.6: cannot open shared object file: No such file or directory`

    Then try the following:
    `sudo apt-get install libsm6 libxrender1 libfontconfig1`

### Docker

You can build a Docker image with (takes ~2-3 hours)

    docker build -t madgrizzle/webcontrol .

Then you can run it directly

    docker run -it -p 5000:5000 -v $HOME/.WebControl:/root/.WebControl --privileged madgrizzle/webcontrol

Or push it up to Docker Hub

    docker push madgrizzle/webcontrol

Note that you'll need to build the Docker image either on an ARM platform (e.g. RaspberryPi), or on a version of Docker that supports ARM emulation (either Docker for Mac or on Linux with binfmt_misc/qemu configured).

### Automatic code formatting

This project uses [black](https://github.com/ambv/black) to automatically format python code. To run the autoformatter, simply install black locally with `pip`.

    pip install black

Subsequently, you can just run `black .` to format all files in the current directory. 

    black .

If you don't have python3.6+ locally (to be able to run `black`), you can run `black` in a Docker container.

    docker run -v $(pwd):/code johnboiles/python-black .

### IDE

#### PyCharm

[PyCharm Community Edition](https://www.jetbrains.com/pycharm/download) is a free, well-featured Python IDE.

With the [File Watchers](https://plugins.jetbrains.com/plugin/7177-file-watchers) and [BlackPycharm](https://plugins.jetbrains.com/plugin/10563-black-pycharm) plugins you can set up your editor to automatically format your code on save. Then you never have to think about code formatting again :tada:

![PyCharm Screenshot](https://user-images.githubusercontent.com/218876/47197011-817e1600-d318-11e8-8172-eb2c1ffe2d21.png)

#### Eclipse PyDev

[Eclipse](https://www.eclipse.org/downloads/packages/) is a free multiplatform IDE for multiple programming languages. Python developement is provided by the free [PyDev plugin](https://www.pydev.org/index.html).

##### Eclipse Configuration

To use a python virtual environment:
* Top Menu -> Windows -> Preferences
* Popup Left menu -> PyDev -> Interpreters -> Python Interpreter
* Click `Browse for Python/Pypy exe` button.
* Navigate to the path of your virtual env (e.g. ~/.venv/bin) and select `python3` executable.
* Name the Interpreter something unique. If this virtual env is just for Webcontrol you can name it `Webcontrol Python3`
* Select all paths listed excluding paths that your Project uses.
* Click `OK`
* A window will appear listing folders to be included in Python Path. They should all be selected. Click `OK`.
* Right click on Project Name 'WebControl' -> Properties -> PyDev - Intepreter/Grammar.
* Select `Intepreter` -> The one you just created (e.g `WebControl Python3`)
* Select `Grammar Version` ->  `Same as interpreter`. 
* Click `Apply and Close` button.

##### Eclipse Debug Configuration

This is required to work with `gevent monkey` as many break point will fail to work without it.
* Top Menu -> Windows -> Preferences
* Popup left menu -> PyDev -> Debug
* Check `Gevent compatible debugging?`
* Click `Apply and Close` button.

Optimizing Cython debugger
* Run the debugger by clicking the `bug` icon
* It should give you a warning that Cython is not optimized and prints out a command like: (DO NOT USE THE FOLLOWING)

    "[PATH TO VIRTUALENV]/bin/python3" "[PATH TO ECLIPSE]/plugins/org.python.pydev.core_7.4.0.201910251334/pysrc/setup_cython.py" build_ext --inplace running build_ext

* Stop the debugger.
* Copy and paste the whole line into Command Prompt/Terminal and run it. 
* It will take a while to compile.
* Start the debugger again. The message should now be gone and debugger runs fast.

##### Eclipse Black code formatter

* Install `black` to virtual environment as described above in `Automatic code formatting`
* Top Menu -> Window -> Preferences
* Popup Left menu -> PyDev -> Editor -> Code Style -> Code Formatter
* Select `Black` from the `Formatter style` drop down.
* Select `Search in interpreter` radio button.
* Click `Apply and close` button.

Open a python file and Top Menu -> Source -> Format Code. Or use keyboard shortcut [Ctrl] + [Shift] + [F].

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

Added to TODO list?

## Authors

* **Madgrizzle** - *Initial work* - [madgrizzle](https://github.com/madgrizzle)
* **John Boiles** - *Docker Expert* - [johnboiles](https://github.com/johnboiles)
* **Tinker** - *UI Improvements/Bug Fixer/Etc.* - [gb0101010101](https://github.com/gb0101010101)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

See [LICENSE](https://github.com/madgrizzle/WebControl/blob/master/LICENSE)
