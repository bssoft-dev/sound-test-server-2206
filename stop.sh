#!/bin/bash
export PORT=`cat config.ini | grep port | awk '{print$3}'`
export REST_PS=`netstat -nltp | grep $PORT | awk {'print$7'} | cut -d '/' -f1`

while [ ! -z $REST_PS ]
do
    echo "Stopping API server."
    kill -9 $REST_PS
    sleep 1
    export REST_PS=`netstat -nltp | grep $PORT | awk {'print$7'} | cut -d '/' -f1`
done
echo "Rest API server is stopped"