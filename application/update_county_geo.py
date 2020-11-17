from app import db
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from models import State, County
from geojson import Point, Feature, FeatureCollection, dump
from sqlalchemy import func
import os
import json

def update_geojson():
    #query all counties
    county_query = db.session.query(County).all()

    #load the mapbox tileset
    script_dir = os.path.dirname(__file__)
    f = open(script_dir + '/json/countyData.geojson', 'r') 
    contents = f.read()
    f.close()
    mapbox_data = json.loads(contents)
    mapbox_dict = mapbox_data['features']

    bad_counties = []

    for county in county_query:
        state_name = county.state.name
        name = county.name
        if name != "Unknown":
            county_list = list(filter(lambda item: item['properties']['STATE'].lower() == state_name.lower() and item['properties']['NAME'].lower() == name.lower(), mapbox_dict))
            if len(county_list) == 0:
                bad_counties.append('{}, {}'.format(name, state_name))
            for county_entry in county_list:
                county_entry['properties']['cases'] = county.new_cases

    with open(script_dir + '/json/countyData.geojson', 'w') as outfile:
        json.dump(mapbox_data, outfile)

    print('unknown: {}'.format(bad_counties))
    print('County geosjon updated.')

if __name__ == '__main__':
    update_geojson()