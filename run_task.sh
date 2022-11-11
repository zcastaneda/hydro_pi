#!/bin/bash

echo "running"
python3 aws_iot.py --endpoint ahc8ri0g3pxso-ats.iot.us-west-2.amazonaws.com \
--rootCA ~/Documents/aws_iot/certs/AmazonRootCA1.pem \
--cert ~/Documents/aws_iot/certs/rasp_pi-certificate.pem.crt \
--key ~/Documents/aws_iot/certs/rasp_pi-private.pem.key \
--thingName rasp_pi \
--clientId rasp_pi