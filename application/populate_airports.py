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

airportID = 0

territories = ["AMERICAN SAMOA", "N MARIANA ISLANDS", "GUAM", "MIDWAY ATOLL",
    "PUERTO RICO", "VIRGIN ISLANDS"]

def assignNewAirportID():
    temp = airportID
    airportID = aiportID + 1
    return temp 

# delete existing entries
# def reset():
#   print('Deleted '+str(Airport.query.delete())+' counties')
#   airportID = 0    

# read excel file as store all info as dataframe
#if using p139 file, there's no need to implement a filter func
airportFile = '.\data\p139certifiedAirports.xlsx'

fileData = pd.read_excel(airportFile)

for index, row in fileData.iterrows():

    stateName = ''
    #check for territories (DC gets modded to virginia)
    if row['State'] in territories:
        break
    elif row['State'] == "DIST. OF COLUMBIA":
        stateName = 'VIRGINIA'
    else:
        stateName = row['State']
    
    try:
        state = State(name= func.lower(stateName))

        county = County(
            name = func.lower(row['County']),
            state = state
        )

        airport = Airport(
            id = assignNewAirportID,
            icao24 = row['IcaoIdentifier'],
            county = county,
            code = func.lower(row['FacilityName'])
        )
        print(row['FacilityName'])
        db.session.add(airport)

    except Exception as e:
        print('ERROR: Unable to add airport ' + str(e))

db.session.commit()


