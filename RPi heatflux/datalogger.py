# -*- coding: utf-8 -*-

# realtime data logger script by Akram Ali
# Updated on 10/05/2021
# Updated on 2/27/2023 by Jackie McAninch

from datetime import datetime
from influxdb import InfluxDBClient
import time
from pathlib import Path
import subprocess
import os

# get hostname of Pi to identify which one it is
hostname = subprocess.check_output('hostname', shell=True).decode('utf-8').strip()

now = datetime.now()   # get current date/time
logging_start_time = now.strftime('%Y-%m-%d_%H%M%S')    # format datetime to use in filename
temp_data_dir = './temp'
data_dir = './data'
server = 'data.elemental-platform.com'
influx_port = 8086
user = 'user'
passwd = 'password'
db = 'database'

time.sleep(10) # sleep 10 seconds to let data come in first

def convert_to_float(string):
    try:
        f = float(string)
        return f
    except ValueError:
        return 0.0


# function to find, parse, log and upload data files
def logdata(_dt):

    # get data from temp file
    try:
        os.makedirs(temp_data_dir, exist_ok=True)
        with open(f'{temp_data_dir}/t.csv','rb') as f:
            dataline = f.readline()
    except Exception as e:
        print(f'(datalogger.py) Failed to open temp file: {e}')
        
    # parse data
    data = []
    for p in dataline.decode('utf-8').strip().split(","): #strip() removes trailing \n
        data.append(p)
    if len(data) != 8:
        print(f'(datalogger.py) Insufficient data from temp file.')
        return
    else:
        print(f'Data read successfully!\n\t{data}')

    # save data to file
    os.makedirs(data_dir, exist_ok=True)
    filename = f'{data_dir}/{hostname}_heatflux_{logging_start_time}.csv'
    my_file = Path(filename)
    if my_file.is_file():   # if file already exists, i.e., logging started
        try:
            with open(filename,'a') as file:   # open file in append mode
                file.write(str(_dt) + ',')   # write formatted datetime
                file.write(",".join(data))
                file.write("\n")
        except Exception as e:
            print(f'(datalogger.py) Error: Failed to open file: {e}')

    
    # file does not exist, write headers to it, followed by data. This should happen first time when creating file only
    else:   
        try:
            with open(filename,'a') as file: # open file in append mode
                file.write('Date/Time')
                for n in range(1,9):
                    file.write(f',{"Temperature (C)" if n%2==0 else "Heat Flux (W/m2)"} (Sensor {n//2})')
        except Exception as e:
            print(f'(datalogger.py) Error: Failed to open file: {e}')
    # start influx session and upload
    try:
        client = InfluxDBClient(server, influx_port, user, passwd, db)
        json_data = []
        # create entry to upload
        for i in range(len(data)):
            # i represents the channel being read
            json_data.append(
                {
                    "measurement": "heatflux" if i%2==0 else "temperature",
                    "tags": {
                        "pi": hostname,
                        "sensor":(i//2)+1
                    },
                    "fields": {
                        "value": convert_to_float(data[i])
                    },
                    "time": int(time.time() * 1000)
                }
            )
        result = client.write_points(json_data, database=db, time_precision='ms', batch_size=8, protocol='json')    
        client.close()
    except Exception as e:
        print(f'Error connecting/uploading to InfluxDB: {e}')


# loop forever
while True:
     # this will log data every second
    time.sleep(1)
    dt = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    logdata(dt)

