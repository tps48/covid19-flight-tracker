import os
import json
import geojson
from flask import Flask, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)


app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import State, County, Airport

@app.route('/')
def index():
    return render_template('/index.html')

@app.route('/map/')
def map():
    return render_template('/covidmap.html')

@app.route('/stateData/')
def stateData():
    script_dir = os.path.dirname(__file__)
    f = open(script_dir + '/json/stateData.geojson', 'r')
    contents = f.read()
    f.close()
    return contents

@app.route('/countyData/')
def countyData():
    script_dir = os.path.dirname(__file__)
    f = open(script_dir + '/json/countyData.geojson', 'r')
    contents = f.read()
    f.close()
    return contents

@app.route('/state/<state>/')
def county_cases(state):
    result = db.session.query(County).join(State).filter(func.lower(State.name) == func.lower(state)).all()
    print(result)
    return str(result)

@app.route('/findAirport/<code>/')
def find_airport(code):
    script_dir = os.path.dirname(__file__)
    
    with open(script_dir + '/json/airportData.geojson', 'r') as f:
        airport_json = json.load(f)
    airport_features = airport_json["features"]

    airport = db.session.query(Airport).filter(func.lower(str(code)) == func.lower(Airport.code)).first()
    if airport is not None:
        return geojson.FeatureCollection(list(filter(lambda entry: entry["properties"]["name"] == airport.code, airport_features)))
    else:
        return "Empty"

@app.route('/casesAt/<code>/')
def cases_at_airport(code):
    try:
        return str(db.session.query(Airport).filter(func.lower(str(code)) == func.lower(Airport.code)).first().county.new_cases)
    except:
        abort(404)

@app.route('/airportInfo/<code>/')
def airport_county(code):
    #try:
    airport = db.session.query(Airport).filter(func.lower(str(code)) == func.lower(Airport.code)).first()
    county_name = airport.county.name
    state_name = airport.county.state.name
    location = '{}, {}'.format(county_name, state_name)
    cases = db.session.query(Airport).filter(func.lower(str(code)) == func.lower(Airport.code)).first().county.new_cases
    dict = {}
    dict["location"] = location
    dict["cases"] = cases
    return dict
    #except:
    #abort(404)

@app.route('/outgoingConnections/<airport_name>/')
def outgoing_router(airport_name):
    script_dir = os.path.dirname(__file__)
    
    #with open(script_dir + '/json/airportData.geojson', 'r') as f:
    #    airport_json = json.load(f)
    #airport_features = airport_json["features"]

    airport = db.session.query(Airport).filter(func.lower(str(airport_name)) == func.lower(Airport.code)).first()
    destinationAirports = []
    airportSet = set()
    outRoutes = airport.outgoing_routes
    for row in outRoutes:
        dict = {}
        dict["code"] = row.dest_airport.code.upper()
        dict["cases"] = row.dest_airport.county.new_cases
        dict["location"] = '{}, {}'.format(row.dest_airport.county.name, row.dest_airport.county.state.name)
        if dict["code"] not in airportSet:
            destinationAirports.append(dict)
            airportSet.add(dict["code"])
    
    #airportConnectionList = list(filter(lambda entry: airport_router_helper(destinationAirports, entry), airport_features))
    #return geojson.FeatureCollection(airportConnectionList)
    return json.dumps(list(destinationAirports))

@app.route('/incomingConnections/<airport_name>/')
def incoming_router(airport_name):
    script_dir = os.path.dirname(__file__)

    #with open(script_dir + '/json/airportData.geojson', 'r') as f:
    #    airport_json = json.load(f)
    #airport_features = airport_json["features"]

    airport = db.session.query(Airport).filter(func.lower(str(airport_name)) == func.lower(Airport.code)).first()
    sourceAirports = []
    airportSet = set()
    inRoutes = airport.incoming_routes
    for row in inRoutes:
        dict = {}
        dict["code"] = row.source_airport.code.upper()
        dict["cases"] = row.source_airport.county.new_cases
        dict["location"] = '{}, {}'.format(row.source_airport.county.name, row.source_airport.county.state.name)
        if dict["code"] not in airportSet:
            sourceAirports.append(dict)
            airportSet.add(dict["code"])
    #airportConnectionList = list(filter(lambda entry: airport_router_helper(sourceAirports, entry), airport_features))
    #return geojson.FeatureCollection(airportConnectionList)
    return json.dumps(list(sourceAirports))
    

def airport_router_helper(airports, airport_entry):
    entryName = airport_entry["properties"]["name"]
    return any( location in entryName for location in airports)

@app.route('/airportData/')
def airports():
    script_dir = os.path.dirname(__file__)
    f = open(script_dir + '/json/airportData.geojson', 'r')
    contents = f.read()
    f.close()
    return contents

@app.route('/airportData/max/<num_cases>/')
def airport_filter_max(num_cases):
    if(num_cases == 0):
        return airports()

    script_dir = os.path.dirname(__file__)
    with open(script_dir + '/json/airportData.geojson', 'r') as f:
        airport_json = json.load(f)
    airport_features = airport_json["features"]
    valid_airport_features = list(filter(lambda entry: airport_filter_max_helper(num_cases, entry), airport_features))
    return geojson.FeatureCollection(valid_airport_features)

def airport_filter_max_helper(num_cases, airport_entry):
    name = airport_entry["properties"]["name"]
    airport = db.session.query(Airport).filter(func.lower(name) == func.lower(Airport.code)).first()
    return airport.county.new_cases <= int(num_cases)

@app.route('/airportData/min/<num_cases>/')
def airport_filter_min(num_cases):
    script_dir = os.path.dirname(__file__)
    with open(script_dir + '/json/airportData.geojson', 'r') as f:
        airport_json = json.load(f)
    airport_features = airport_json["features"]
    valid_airport_features = list(filter(lambda entry: airport_filter_min_helper(num_cases, entry), airport_features))
    return geojson.FeatureCollection(valid_airport_features)

def airport_filter_min_helper(num_cases, airport_entry):
    name = airport_entry["properties"]["name"]
    airport = db.session.query(Airport).filter(func.lower(name) == func.lower(Airport.code)).first()
    return airport.county.new_cases >= int(num_cases)

@app.route('/airportData/minMax/<min_cases>/<max_cases>/')
def airport_filter_min_max(min_cases, max_cases):
    script_dir = os.path.dirname(__file__)
    with open(script_dir + '/json/airportData.geojson', 'r') as f:
        airport_json = json.load(f)
    airport_features = airport_json["features"]
    valid_airport_features = list(filter(lambda entry: airport_filter_min_max_helper(min_cases, max_cases, entry), airport_features))
    return geojson.FeatureCollection(valid_airport_features)

def airport_filter_min_max_helper(min_cases, max_cases, airport_entry):
    name = airport_entry["properties"]["name"]
    airport = db.session.query(Airport).filter(func.lower(name) == func.lower(Airport.code)).first()
    county = airport.county
    return county.new_cases >= int(min_cases) and county.new_cases <= int(max_cases)

if __name__ == '__main__':
    app.run()