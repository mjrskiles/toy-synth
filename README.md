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


## Running

### Windows

Make sure moquitto is running:

cd into 'C:\Program Files\mosquitto' in a new PowerShell window

```.\mosquitto.exe```

Then in another PowerShell window:

cd into your project directory

```python src/main.py```

To publish a message
---

From the 'C:\Program Files\mosquitto' dir:

```.\mosquitto_pub -t "synth/test" -m "<your message>"```

# Architecture

## Modules

synth
---

communication
---

configuration
---


## Ideas / discussion

How are we going to communicate between threads?
- I wanted to use MQTT but that would introduce a dependency on having a broker
    - It seems like it wouldn't be easy to build your own broker
- Mailboxes?
- Queues?

What does the general shape of a synth command look like?
Json?
{
    payload: {
        command:  "note_on",
        params: {
            note: 60
            velocity: 1.0
        }
    }
}

What commands can the synth take?

(command - params)
note on - note, velocity
note off - note

## API

### Topics

All topics should begin with toy/

toy/exit
---
Sending anything on this topic should cause the toy synth program to exit gracefully. Not implemented yet (4/9/23)

toy/log
---
Messages sent on this topic will be printed out on the console

