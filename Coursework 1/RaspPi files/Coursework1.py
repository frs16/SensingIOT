#----FRANCESCA SUER - Sensing and IoT Coursework 1 - 01 December 2019----
#----Addresses a BH1750 Light Sensor and the TomTom API----
#----Light Sensor code adapted from Matt Hawkins' BH1750 script----

#----Outputs data every 2 minutes to a CSV and Google Drive----
#----Creates a new CSV every 12 hours----

#----function imports----
import requests
import json
import time
import smbus
import gspread
import csv
import sys
import os
from statistics import mean
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

#----connect to Google Drive API----
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
client = gspread.authorize(creds)

#----open the worksheet----
sheet = client.open("IoT_Data_Google_Sheet").sheet1

#----set up the light sensor and define some constants from the datasheet----
DEVICE     = 0x23 # Default device I2C address
POWER_DOWN = 0x00 # No active state
POWER_ON   = 0x01 # Power on
RESET      = 0x07 # Reset data register value

# Start measurement at 4lx resolution. Time typically 16ms.
CONTINUOUS_LOW_RES_MODE = 0x13

# Start measurement at 1lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_1 = 0x10

# Start measurement at 0.5lx resolution. Time typically 120ms
CONTINUOUS_HIGH_RES_MODE_2 = 0x11

# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_1 = 0x20

# Start measurement at 0.5lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_HIGH_RES_MODE_2 = 0x21

# Start measurement at 1lx resolution. Time typically 120ms
# Device is automatically set to Power Down after measurement.
ONE_TIME_LOW_RES_MODE = 0x23

bus = smbus.SMBus(1)  # Rev 2 Pi uses 1

def convertToNumber(data):
  # Simple function to convert 2 bytes of data
  # into a decimal number. Optional parameter 'decimals'
  # will round to specified number of decimal places.
  result=(data[1] + (256 * data[0])) / 1.2
  return (result)

def readLight(addr=DEVICE):
  # Read data from I2C interface
  data = bus.read_i2c_block_data(addr,ONE_TIME_HIGH_RES_MODE_1)
  return convertToNumber(data)

#----create function for data collection----
def main():
    csvtitle = 'output.csv'
    title_iterator = 1
    start_time = time.time()
    save_timer = time.time()
    loop = 0
    
    while True:
     
        #----obtain and average light levels over a 2 minute period----
        twominuteslight = []
        twominutes = 120

        #----define timer start----
        timer = time.time()
        
        #----set the function to collect the light level every 5 seconds and output an average after 2 minutes----
        while True:
            current_light = readLight()
            duration = time.time() - timer
            twominuteslight.append(current_light)
            time.sleep(5) 

            #----check to see if 2 minutes has passed, if so break loop----
            if duration > twominutes:
                break

        #----output the average light level from the last 2 minutes----
        ave_light_level = round(mean(twominuteslight),2)  

        #----request routing data from TomTom API----
        x = requests.get("https://api.tomtom.com/routing/1/calculateRoute/*INSERT LOCATION*%2C-*INSERT LOCATION*%3A*INSERT LOCATION*%2C-*INSERT LOCATION*/json?maxAlternatives=1&language=python&computeTravelTimeFor=all&routeType=fastest&avoid=unpavedRoads&travelMode=bus&key=*INSERT API KEY*")
        y = requests.get("https://api.tomtom.com/routing/1/calculateRoute/*INSERT LOCATION*%2C-*INSERT LOCATION*%3A*INSERT LOCATION*%2C-*INSERT LOCATION*/json?maxAlternatives=1&language=python&computeTravelTimeFor=all&routeType=fastest&avoid=unpavedRoads&travelMode=car&key=*INSERT API KEY*")

        bus = x.text
        car = y.text

        parsed_bus = json.loads(bus)
        parsed_car = json.loads(car)

        #----extract necessary data (journey duration)----
        journey_duration_bus = parsed_bus["routes"][0]["summary"]["travelTimeInSeconds"]
        journey_duration_car = parsed_car["routes"][0]["summary"]["travelTimeInSeconds"]

        #----determine departure time----
        current_time = datetime.now()
        departure_date = current_time.strftime("%d/%m/%Y")
        departure_time = current_time.strftime("%H:%M:%S")
        
        #----generate csv output data----
        outputstring = (str(departure_date) + "," + str(departure_time) + "," + str(journey_duration_bus) + "," + str(journey_duration_car) + "," +str(ave_light_level))
        csvData = [(departure_date),(departure_time),(journey_duration_bus),(journey_duration_car),(ave_light_level)]
                    
        #----write to a local CSV----
        with open(os.path.join(sys.path[0], csvtitle), 'a') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(csvData)

        #----write values to the google sheet----
        row = [str(outputstring)]
        index = 1
        sheet.insert_row(row, index)

        #----print data to shell to check what's going on----
        print ("The current time is " + str(departure_date) + " " + str(departure_time))
        print ("=======================================")
        print ("")
        print ("The journey will take " + str(journey_duration_bus) + " seconds by bus and " + str(journey_duration_car) + " seconds by car at on " + str(departure_date) + " at " + str(departure_time))
        print (" ")
        print ("The average light level over the last two minutes was " + str(ave_light_level) + " Lux")
        print (" ")
        print ("The current filename to which we are writing is " + str(csvtitle))
        print (" ")
        print ("The data we have saved to " + str(csvtitle) + " and outputted to Google Drive is", outputstring)
        print (" ")

        #----check to see if 12 hours has passed and iterate the file name----
        twelve_hours = 60*60*12
        save_time_passed = time.time() - save_timer
        
        if save_time_passed > twelve_hours:
            #----reset the save timer----
            save_timer = time.time()
            
            #----set the next output file name (iterate)----
            csvtitle = 'output' + str(title_increment) + '.csv'
            title_increment = title_increment + 1

        #----increment the loop counter----
        loop = loop + 1

if __name__ == "__main__":
    main()