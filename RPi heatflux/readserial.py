# -*- coding: utf-8 -*-

# This script initializes Fluxteq's Compaq DAQ,
# reads data from serial port and saves to temporary file

# Developed by Akram Ali
# Updated on: 10/21/2020

import time
import serial
import os

number_of_sensors = '4' # set number of sensors connected to Compaq DAQ
sensitivities = ['1.08', '1.09', '1.00', '1.05']    # set sensitivities for each sensor based on its calibration sheet. First one is channel 0
temp_data_dir = './temp'

# initialize serial port
try:
    serialport = serial.Serial('/dev/ttyUSB0', 9600, timeout=10) # make sure baud rate is the same
    time.sleep(3)  # wait few seconds till serial port initialized
except serial.SerialException:
    print('Serial Port Failed.')
    while True:     # loop forever
        time.sleep(1)


# send initial configuration to the DAQ to begin logging
try:
    serialport.write(bytes(number_of_sensors, 'utf-8'))
    time.sleep(1.5)
    for n in range(int(number_of_sensors)):
        serialport.write(bytes(sensitivities[n], 'utf-8'))
        time.sleep(1.5)
    time.sleep(1)
except Exception as e:
    print(f'Failed to write data: {e}')


# loop forever
while True:
    time.sleep(0.01)    # wait a bit so CPU doesn't choke to def
    data = serialport.read(1)   # get first byte from serial port
    n = serialport.in_waiting   # check remaining number of bytes
    if n:    # wait till data arrives and then read it
        data = data + serialport.readline()    # read one line and merge with first byte
        try:
            with open(f'{temp_data_dir}/t.csv','wb') as f:
                f.write(data)     # save data in a temp csv file
        except Exception as e:
            print(f'Error opening temp file: {e}')

