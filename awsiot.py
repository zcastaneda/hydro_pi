
# from adafruit_seesaw.seesaw import Seesaw
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
# from board import SCL, SDA

import logging
import time
import json
import argparse
import busio
import board
import adafruit_dht
import RPi
import sys
import subprocess
from aws_iot import ds18b20


# Shadow JSON schema:
#
# {
#   "state": {
#       "desired":{
#           "moisture":<INT VALUE>,
#           "temp":<INT VALUE>            
#       }
#   }
# }

# Function called when a shadow is updated
def customShadowCallback_Update(payload, responseStatus, token):

    # Display status and data from update request
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("moisture: " + str(payloadDict["state"]["reported"]["moisture"]))
        print("air_temperature: " + str(payloadDict["state"]["reported"]["air_temp"]))
        print("water_temperature: " + str(payloadDict["state"]["reported"]["water_temp"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

# Function called when a shadow is deleted
def customShadowCallback_Delete(payload, responseStatus, token):

     # Display status and data from delete request
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")

    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")


# Read in command-line parameters
def parseArgs():

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your device data endpoint")
    parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
    parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
    parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
    parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicShadowUpdater", help="Targeted client id")

    args = parser.parse_args()
    return args


# Configure logging
# AWSIoTMQTTShadowClient writes data to the log
def configureLogging():

    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

if __name__ == "__main__":

    # Parse command line arguments
    args = parseArgs()

    if not args.certificatePath or not args.privateKeyPath:
        parser.error("Missing credentials for authentication.")
        exit(2)

    # If no --port argument is passed, default to 8883
    if not args.port: 
        args.port = 8883


    # Init AWSIoTMQTTShadowClient
    myAWSIoTMQTTShadowClient = None
    myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(args.clientId)
    myAWSIoTMQTTShadowClient.configureEndpoint(args.host, args.port)
    myAWSIoTMQTTShadowClient.configureCredentials(args.rootCAPath, args.privateKeyPath, args.certificatePath)

    # AWSIoTMQTTShadowClient connection configuration
    myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10) # 10 sec
    myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5) # 5 sec

    #initialize sensors
    print('setting up devices')
    bash_cmd = f'chmod 777 /dev/mem'
    process = subprocess.Popen(bash_cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    bash_cmd = f'chmod 777 /dev/gpiomem'
    process = subprocess.Popen(bash_cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    

    dht22_1 = adafruit_dht.DHT22(board.D4)
    water_temp1 = ds18b20.pyds18b20()
    print(f'current devices: {water_temp1.device_list}')


    # Connect to AWS IoT
    print('connecting to AWS')
    myAWSIoTMQTTShadowClient.connect()
    print('connected to AWS')

    # Create a device shadow handler, use this to update and delete shadow document
    print('creating shadow handler')
    deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(args.thingName, True)
    print('created shadow handler')

    # Delete current shadow JSON doc
    print('deleting current shadow JSON doc')
    deviceShadowHandler.shadowDelete(customShadowCallback_Delete, 15)

    print('deleted current shadow JSON doc')
    # Read data from moisture sensor and update shadow
    while True:
        print('while loop')

        reading_dht22 = True
        reading_temp=True
        reading_humidity=True

        while reading_dht22:
            try:
                if reading_humidity:
                    humidity = dht22_1.humidity
                    reading_humidity=False

                if reading_temp:
                    # read temperature from the temperature sensor
                    temperature_f = round(dht22_1.temperature*(9/5)+32,3)
                    reading_temp=False
                reading_dht22=False
            except Exception as e:
                print(f'{e}. Retrying dht22')
        try:


            # get water temp from ds18b20
            water_temp_f = round(water_temp1.get_temp(sensor_name = water_temp1.device_list[0]),3)

            # Display moisture and temp readings
            print("Moisture Level: {}".format(humidity))
            print("Temperature: {}".format(temperature_f))
            print("Water temperature: {}".format(water_temp_f))

            
            # Create message payload
            payload = {"state":{"reported":{"moisture":str(humidity),"air_temp":str(temperature_f),"water_temp":str(water_temp_f)}}}

            # Update shadow
            deviceShadowHandler.shadowUpdate(json.dumps(payload), customShadowCallback_Update, 5)
        except Exception as e:
            print(e)
            next
        time.sleep(10)