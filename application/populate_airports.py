import requests
import json
import sys
from app import db
from models import Flight, Airport, County, State
from pandas import DataFrame, read_excel
import pandas as pd 
import xlrd
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
#from Sets import set

print('Populating airports')
print('Deleted '+str(Airport.query.delete())+' airports')
airportID = 0

territories = ["AMERICAN SAMOA", "N MARIANA ISLANDS", "GUAM", "MIDWAY ATOLL",
    "PUERTO RICO", "VIRGIN ISLANDS", "AMERICAN"]

# delete existing entries
# def reset():
#   print('Deleted '+str(Airport.query.delete())+' counties')
#   airportID = 0    

# read excel file as store all info as dataframe
#if using p139 file, there's no need to implement a filter func
airportFile = open('./application/data/p139certifiedAirports.xlsx','rb')
state_set = set()

fileData = pd.read_excel(airportFile)

for index, row in fileData.iterrows():

    stateName = ''
    #check for territories (DC gets modded to virginia)
    if row['StateName'] not in territories:

        if row['StateName'] == "DIST. OF COLUMBIA":
            stateName = 'DISTRICT OF COLUMBIA'
        else:
            stateName = row['StateName']
            state_set.add(stateName)
        
        try:

            airportState = db.session.query(State).filter(func.lower(State.name) == func.lower(stateName)).all()
            if len(airportState) > 0:
                airportState = airportState[0]
                print('State: ' + airportState.name)
                
                countyName = row['County']
                print(countyName)
                airportCounty = db.session.query(County).filter(County.state_id == airportState.id).filter(func.lower(County.name) == func.lower(countyName)).all()
                if len(airportCounty) > 0:
                    airportCounty = airportCounty[0]
                    print('County: ' + airportCounty.name)
                    arp_latitude = row['ARPLatitudeS']
                    arp_longitude = row['ARPLongitudeS']
                    lat = float(arp_latitude[0:11])/3600
                    if arp_latitude[11] == 'S':
                        lat *= -1

                    longt = float(arp_longitude[0:11])/3600
                    if arp_longitude[11] == 'W':
                        longt *= -1

                    airport = Airport(
                        icao24 = row['IcaoIdentifier'],
                        county_id = airportCounty.id,
                        code = func.lower(row['LocationID'][1:]),
                        latitude = lat,
                        longitude = longt
                    )

                    print(row['FacilityName'])
                    db.session.add(airport)

        except Exception as e:
            print('ERROR: Unable to add airport ' + str(e))

db.session.commit()
print('{} states'.format(len(state_set)))


