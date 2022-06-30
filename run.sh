#!/bin/bash
export logpath=`cat config.ini | grep log_path | awk '{print$3}'`
python3 app.py &> ${logpath}/log.txt &
echo "Server started"