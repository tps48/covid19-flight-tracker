from app import db
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from models import State
from geojson import Point, Feature, FeatureCollection, dump
from sqlalchemy import func
import os
import json

def update_geojson():
    #query all states
    state_query = db.session.query(State).all()

    #load the mapbox tileset
    script_dir = os.path.dirname(__file__)
    f = open(script_dir + '/json/stateData.geojson', 'r') 
    contents = f.read()
    f.close()
    mapbox_data = json.loads(contents)
    mapbox_dict = mapbox_data['features']

    for state in state_query:
        print(state.name)
        state_dict = list(filter(lambda item: item['properties']['name'] == state.name, mapbox_dict))[0]
        state_dict['properties']['cases'] = state.new_cases

    with open(script_dir + '/json/stateData.geojson', 'w') as outfile:
        json.dump(mapbox_data, outfile)

    print('State geosjon updated.')

if __name__ == '__main__':
    update_geojson()