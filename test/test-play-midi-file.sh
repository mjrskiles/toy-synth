file=$1
if [ -z "$1" ]; then
    echo "No file name supplied. Using default file."
    file="./test/midi-files/zelda1-dungeon1.mid"
fi

play() {
    mosquitto_pub -t "toy/midi/player" -m "play -f ${file}"
}

quit() {
    mosquitto_pub -t "toy/exit" -m "exit"
}

source ./venv/bin/activate
(python -m toysynth)&

sleep 3

play

sleep 300

echo "Sending shutdown command to toy synth"
quit
