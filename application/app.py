import os
import json
from flask import Flask, render_template
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

@app.route('/stateData')
def stateData():
    script_dir = os.path.dirname(__file__)
    f = open(script_dir + '/json/stateData.geojson', 'r')
    contents = f.read()
    f.close()
    return contents

@app.route('/countyData')
def countyData():
    script_dir = os.path.dirname(__file__)
    f = open(script_dir + '/json/countyData.geojson', 'r')
    contents = f.read()
    f.close()
    return contents

@app.route('/airportData')
def airports():
    script_dir = os.path.dirname(__file__)
    f = open(script_dir + '/json/airportData.geojson', 'r')
    contents = f.read()
    f.close()
    return contents

@app.route('/state/<state>')
def county_cases(state):
    result = db.session.query(County).join(State).filter(func.lower(State.name) == func.lower(state)).all()
    print(result)
    return str(result)


if __name__ == '__main__':
    app.run()