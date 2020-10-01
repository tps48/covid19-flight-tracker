import requests
import json
import sys
from app import db
from models import Flight
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

flightID = 0

def assignNewFlightID():
    temp = flightID
    flightID = flightID + 1
    return temp 

#Class for storing/translating data
class FlightTemplate:
    def __init__(icao, callsign, lon, lat, on_g, true_t):
        self.icao = icao
        self.callsign = callsign
        self.lon = lon
        self.lat = lat
        self.on_g = on_g
        self.true_t = true_t 
  

# delete existing entries
print('Deleted '+str(Flight.query.delete())+' flights')

# 1st REST API call to OpenSky
flightsAroundUSA = json.loads(requests.get('https://seniorProjectDJT:gimmeFlightInf0@opensky-network.org/api/states/all?lamin=22.8389&lomin=-168.9962&lamax=71.8229&lomax=-61.5226').text)

#create temp list to store valid flights
validFlightList = []
stateVectors = flightsAroundUSA['states']
for vector in stateVectors:
    if vector[2] == 'United States':
        validFlightList.append( FlightTemplate(vector[0], vector[1], vector[5], vector[6], vector[8], vector[10]) )

#Time constraint of 15 minutes
end = datetime.datetime.now()
begin = end - datetime.timedelta(minutes=15)
endEpoch = int(end.timestamp() * 1000)
beginEpoch = int(begin.timestamp() *1000)

currentFlights = json.loads(requests.get('https://seniorProjectDJT:gimmeFlightInf0@opensky-network.org/api/flights/all?begin=1517227200&end=1517230800').text)
# Loop through 2nd query
for flightObj in currentFlights:
    #Look through valid flights for a match
    for temp in validFlightList:
        if temp.icao == flightObj['icao24']:

            try:
                dAirport = db.session.query(Airport).filter(func.lower(Airport.icao24) == func.lower(flightObj['estDepartureAirport'])).one()
                aAirport = db.session.query(Airport).filter(func.lower(Airport.icao24) == func.lower(flightObj['estArrivalAirport'])).one() 
                flight = Flight(
                    id = assignNewFlightID()
                    flight_number = callsign
                    departing_airport_id = dAirport.id
                    arriving_airport_id = aAirport.id
                    depature_time = flightObj['firstSeen']
                    expected_arrival_time = flightObj['lastSeen']
                    latitude = temp.lat 
                    longitude = temp.lon
                    delayed = temp.on_g #Want changed to on_ground
                    on_route = true #Want this one removed
                    #true_tracks = temp.true_t (float)
                    last_updated = datetime.datetime.now().timestamp()
                )
                db.session.add(flight)
            except Exception as e:
                print('ERROR: Unable to add flight for the state ' + str(flightObj) + ': ' + str(temp))

            db.session.commit()
