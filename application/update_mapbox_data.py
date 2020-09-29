import requests
import json
import sys
import os
from app import db
from models import Flight, Airport, County, State

#load the mapbox tileset
script_dir = os.path.dirname(__file__)
f = open(script_dir + '/json/stateData.geojson', 'r')
contents = f.read()
f.close()
mapbox_data = json.loads(contents)
print(len(mapbox_data['features']))