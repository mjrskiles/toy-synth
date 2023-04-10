#!/bin/bash
freq=0.0
note_on() {
    mosquitto_pub -t "toy/synth/test/command" -m "note_on -f ${freq}"
}

note_off() {
    mosquitto_pub -t "toy/synth/test/command" -m "note_off"
}

quarter_len=0.1
half_len=0.2
whole_len=0.4

source ./venv/bin/activate
(python -m toysynth)&
pid=$!

sleep 1
freq=739.99
note_on
sleep $quarter_len
freq=698.46
note_on
sleep $quarter_len
freq=587.33
note_on
sleep $quarter_len
freq=415.30
note_on
sleep $quarter_len
freq=392.00
note_on
sleep $quarter_len
freq=622.25
note_on
sleep $quarter_len
freq=783.99
note_on
sleep $quarter_len
freq=987.77
note_on
sleep $quarter_len
note_off

echo "Killing $!"
kill $pid