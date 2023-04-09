#!/bin/bash
freq=0.0
note_on() {
    mosquitto_pub -t "toy/synth/test/command" -m "note_on -f ${freq}"
}

note_off() {
    mosquitto_pub -t "toy/synth/test/command" -m "note_off"
}

quarter_len=0.25
half_len=0.5
whole_len=1.0

source ../../venv/bin/activate
(python ../../src/main.py)&
pid=$!

sleep 1
freq=220.0
note_on
sleep $half_len
freq=440.0
note_on
sleep $half_len
freq=220.0
note_on
sleep $half_len
note_off

echo "Killing $!"
kill $pid