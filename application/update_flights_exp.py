import requests
import json
import sys
import datetime
from app import db
from models import Flight, Airport
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

#Class for storing/translating data
class FlightTemplate:
    def __init__(self, icao, callsign, lon, lat, on_g, true_t):
        self.icao = icao
        self.callsign = callsign
        self.lon = lon
        self.lat = lat
        self.on_g = on_g
        self.true_t = true_t 

    def __repr__(self):
        return self.icao
  

# delete existing entries
print('Deleted '+str(Flight.query.delete())+' flights')

# 1st REST API call to OpenSky
flightsAroundUSA = json.loads(requests.get('https://seniorProjectDJT:gimmeFlightInf0@opensky-network.org/api/states/all?lamin=22.8389&lomin=-168.9962&lamax=71.8229&lomax=-61.5226').text)

#create temp list to store valid flights
validFlightList = []
stateVectors = flightsAroundUSA['states']
for vector in stateVectors:
    #print(vector)
    if vector[2] == 'United States':
        validFlightList.append(FlightTemplate(vector[0], vector[1], vector[5], vector[6], vector[8], vector[10]) )

#Time constraint of 15 minutes
end = datetime.datetime.now()
begin = end - datetime.timedelta(minutes=60)
endEpoch = int(end.timestamp())
beginEpoch = int(begin.timestamp())

print(validFlightList[0].icao)
string = 'https://seniorProjectDJT:gimmeFlightInf0@opensky-network.org/api/flights/aircraft?icao24={}&begin={}&end={}'.format(validFlightList[0].icao,beginEpoch,endEpoch)
print(string)
flight = json.loads(requests.get('https://seniorProjectDJT:gimmeFlightInf0@opensky-network.org/api/flights/aircraft?icao24={}&begin={}&end={}'.format(validFlightList[0].icao,beginEpoch,endEpoch)).text)
print(flight)