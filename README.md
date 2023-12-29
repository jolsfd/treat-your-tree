# TreatYourTree

## Description

A smart sensor that tracks the water level of your Christmas tree. When the tree needs water, the sensor plays the melody of "O Tannenbaum", causes a lamp with a Shelly relay and a red LED to flash.

## Shopping List

* passive buzzer
* cables
* water sensor
* 220 ohm resistor
* red led
* rasperry pi pico w
* zip ties
* christmas tree

## Setup

1. Clone the repository.
2. Assemble the necessary circuits for the sensor.
3. Replace the wifi credentials in ```boot.py``` with your own credentials.
4. Flash all ```.py``` files to the raspberry pico w.
5. Enter the ip adress fro ypur shelly relay/bulb in the ```main.py``` file.
6. Setup webrepl for remote debugging/development.

## Usage

* default ip adress in access point mode: 192.168.4.1
* port number for webrepl :8266
* get data from sensor ```http://HOST_IP:80/```
* shutdown command for webserver ```http://HOST_IP:80/shutdown```