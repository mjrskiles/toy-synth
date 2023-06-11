## Environment Setup

### Windows

You must have Eclipse mosquitto installed!

Go to https://mosquitto.org/download/ and download the latest version of mosquitto

Right click the installer and run as administrator

clone the repository

make sure you have python 3.10 or higher installed

```pip3 install virtualenv```

cd into the project directory wherever you cloned it

```python -m virtualenv venv```

NOTE: For the virtual environment activate command to work, you may have to run your PowerShell as administrator and run

```Set-ExecutionPolicy -ExecutionPolicy Unrestricted```

then

```.\venv\Scripts\activate```

```python -m pip install -r windows.txt```

### Mac

brew install portaudio

### Linux (Ubuntu 22.04)

We'll need to install a few necessary packages onto the system first:

```sudo apt install mosquitto```

```sudo apt-get install pkg-config```

```sudo apt-get install portaudio19-dev```

```sudo apt-get install libjack-jackd2-dev libasound2-dev```

clone the repository and cd into the project directory

make sure you have pip3 installed:

```which pip3```

if it returns nothing, try:

```sudo apt install python3-pip```

then

```pip3 install virtualenv```

```python3 -m virtualenv venv```

You should now have a folder called venv in the project directory. Let's active it:

```source ./venv/bin/activate```

install the dependencies into the virtual environment:

```pip3 install -r requirements.txt```


## Running

### Windows

Make sure mosquitto is running:

cd into 'C:\Program Files\mosquitto' in a new PowerShell window

```.\mosquitto.exe```

Then in another PowerShell window:

cd into your project directory

(your virtual env should be activated)

```python -m toysynth```

To publish a message
---

From the 'C:\Program Files\mosquitto' dir:

```.\mosquitto_pub -t "toy/log" -m "<your message>"```

```.\mosquitto_pub -t "toy/midi/player" -m "play -f ./test/midi-files/zelda1-dungeon1.mid"```

```.\mosquitto_pub -t "toy/exit" -m "exit"```

### Mac

Start mosquitto

```/usr/local/sbin/mosquitto -c /usr/local/etc/mosquitto/mosquitto.conf```


## API

### Topics

All topics should begin with toy/

toy/exit
---
Sending anything on this topic should cause the toy synth program to exit gracefully.

toy/log
---
Messages sent on this topic will be printed out on the console

