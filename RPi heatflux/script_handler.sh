#!/bin/bash
script_dir=$(echo "$0" | rev | cut -d '/' -f 2- | rev)
while true; do
    python "$script_dir/readserial.py" &
    python "$script_dir/datalogger.py" &
    wait $!
    sudo killall python
    sleep 10
done
exit
