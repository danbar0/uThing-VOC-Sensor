# Continuation of code written for the uThing VOC sensor
# Based on a guide from:
# https://www.hackster.io/damancuso/indoor-air-quality-monitor-b181e9

import time, sys, json
from influxdb import InfluxDBClient
import serial
import psutil

databaseName = 'airquality'
debug = False

appended_data = {'cpuTemperature': 'value'}
json_message = [{
    "measurement": "humidity",
    "fields": {
        "value": 12.34
    }
}]
influxClient = InfluxDBClient('raspberrypi.local', 8086, 'user', 'password', databaseName)

def serialToInflux():
    while True:
        try:
            message = ""
            #uart = serial.Serial('/dev/tty.usbmodem14101', 115200, timeout=11) # (MacOS)
            uart = serial.Serial('/dev/ttyACM0', 115200, timeout=11) # Linux
            uart.write(b'J\n')


        except:
            if debug is True:
                print("Error opening uart")
            break

        while True:
            time.sleep(1)
            cpu_temperature = psutil.sensors_temperatures()
            cpu_temperature = str(cpu_temperature.values())
            cpu_temperature = cpu_temperature[40:42]

            try:
                message = uart.readline()
                uart.flushInput()
                if debug is True:
                    print(message)
            except:
                if debug is True:
                    print("Error")

            try:
                data_dict = json.loads(message.decode())
                appended_data['cpuTemperature'] = str(cpu_temperature)
                data_dict.update(appended_data)
                if debug is True:
                    print(data_dict)

                for measurement, value in data_dict.items():
                    json_message[0]['measurement'] = measurement
                    json_message[0]['fields']['value'] = float(value)
                    if debug is True:
                        print(json_message)
                    try:
                        if debug is False:
                            influxClient.write_points(json_message)
                    except OSError as e:
                        if debug is True:
                            print("Unable to write to InfluxDB: %s" % e)

            except ValueError:
                if debug is True:
                    print("Value Error on received or parsing data!")
            except IndexError:
                if debug is True:
                    print("Index Error on received or parsing data!")


if __name__ == "__main__":
    serialToInflux()

