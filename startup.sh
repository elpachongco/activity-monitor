#!/bin/bash
# To run the programs at startup, see `README.md`
python3 ./main.py &
echo $!
cd ./dashboard/client/
flask run -p 9000 --host 0.0.0.0 --debug & 
echo $!
