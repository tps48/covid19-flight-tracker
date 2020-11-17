import requests
import json
import sys
import os
from app import db
from models import Flight, Airport, County, State, Route
from pandas import DataFrame, read_csv
import pandas as pd 
import xlrd
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

script_dir = os.path.dirname(__file__)
f = open(script_dir + '/data/routes.csv', 'r')
routes = pd.read_csv(f)
routes_added = 0

print('Populating routes')
print('Deleted '+str(Route.query.delete())+' routes')
print('Working...')

for index, row in routes.iterrows():
    try:
        source = db.session.query(Airport).filter(func.lower(row['Source airport']) == func.lower(Airport.code)).first()
        dest = db.session.query(Airport).filter(func.lower(row['Destination airport']) == func.lower(Airport.code)).first()

        if source is not None and dest is not None:
            route = Route (
                source_airport = source,
                dest_airport = dest
                )
            db.session.add(route)
            routes_added += 1
    except Exception as e:
        print('ERROR: Unable to add route ' + str(e))

db.session.commit()

print('Routes added: {}'.format(routes_added))