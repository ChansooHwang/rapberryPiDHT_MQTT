import asyncio
import logging
import random
import time
from pytz import timezone
from datetime import datetime

import sys
import json
import RPi.GPIO as GPIO
import Adafruit_DHT
import os

import awsiot.greengrasscoreipc
from awsiot.greengrasscoreipc.model import (
    QOS,
    PublishToIoTCoreRequest
)
TIMEOUT = 10

ipc_client = awsiot.greengrasscoreipc.connect()

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger.info("Start Program")

def getSensorData():
    RH, T = Adafruit_DHT.read_retry(Adafruit_DHT.DHT11, 23)
    return (str(RH), str(T))
 
def publishMessage_mqtt(mqtt_topic, payload):
    try:
        
        message = json.dumps(payload)
        qos = QOS.AT_LEAST_ONCE

        request = PublishToIoTCoreRequest()
        request.topic_name = mqtt_topic
        request.payload = bytes(message, "utf-8")
        request.qos = qos
        operation = ipc_client.new_publish_to_iot_core()
        operation.activate(request)
        future = operation.get_response()
        future.result(TIMEOUT)

    except Exception as e:
        logging.info("Publish MQTT Message Error : {0}, topic : {1}, payload : {2}".format(str(e), mqtt_topic, message))


def main():
    logger.info("{0} - Start Publishing MQTT message".format(datetime.now(timezone('Asia/Seoul')).strftime('%Y%m%d%H%M%S')))

    while True:
        try:
            dic_data = {}
            dic_data["time_stamp"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dic_data["timestamp_kst"] = datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d %H:%M:%S')
            RH, T = getSensorData()
            dic_data["RH"] = RH
            dic_data["T"] = T

            publishMessage_mqtt(topic_header, dic_data)
            
            time.sleep(10)

        except asyncio.TimeoutError:
            logger.info("{0} - Timed out while executing".format(datetime.now(timezone('Asia/Seoul')).strftime('%Y%m%d%H%M%S')))
        except Exception as e:
            logger.info("Exception while running : " + repr(e))
    

if __name__ == "__main__":
    global topic_header
    print("Start Program with parameters(TOPIC Header) : ", sys.argv[1])

    topic_header = sys.argv[1]
    print('mqtt : ' + topic_header)
    main()