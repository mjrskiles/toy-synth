## Environment Setup

pip3 install virtualenv

virtualenv venv

brew install portaudio  --mac only?


# Architecture

## Modules

Synth
---

Input
---
- Maybe there should be a command interpreter layer before the synth that can dispatch commands to the correct modules
    - would each command need a channel?
    - this would be useful for handling commands like 'quit' that aren't really sound related
    
MIDI?
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
