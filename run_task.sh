#!/bin/bash

echo "running"
which python3
poetry run python awsiot.py --endpoint ahc8ri0g3pxso-ats.iot.us-west-2.amazonaws.com \
--rootCA /home/zack/Documents/aws_iot/certs/AmazonRootCA1.pem \
--cert /home/zack/Documents/aws_iot/certs/rasp_pi-certificate.pem.crt \
--key /home/zack/Documents/aws_iot/certs/rasp_pi-private.pem.key \
--thingName rasp_pi \
--clientId rasp_pi
