import requests
import json
import sys
import os
from app import db
from models import Route, Flight, Airport, County, State
from sqlalchemy import func

#names of all states for db entry
state_names = ["Alaska", "Alabama", "Arkansas", "Arizona", "California", "Colorado", "Connecticut", "District of Columbia",
    "Delaware", "Florida", "Georgia", "Hawaii", "Iowa", "Idaho", "Illinois", "Indiana", "Kansas", "Kentucky", "Louisiana", "Massachusetts", 
    "Maryland", "Maine", "Michigan", "Minnesota", "Missouri", "Mississippi", "Montana", "North Carolina", "North Dakota", "Nebraska", "New Hampshire", 
    "New Jersey", "New Mexico", "Nevada", "New York", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", "Rhode Island", "South Carolina", "South Dakota", 
    "Tennessee", "Texas", "Utah", "Virginia", "Vermont", "Washington", "Wisconsin", "West Virginia", "Wyoming"]

#hashable county class used for dicts
class CountyTemplate:
    def __init__(self, county_name, state_name):
        self.county_name = county_name
        self.state_name = state_name

    def __hash__(self):
        return hash(self.county_name) ^ hash(self.state_name)

    def __repr__(self):
        return '{}, {}'.format(self.county_name, self.state_name)

    def __eq__(self, other):
        return self.county_name == other.county_name and self.state_name == other.state_name

def populate_states():
    print('clearing database')
    # delete existing entries
    print('Deleted '+str(Route.query.delete())+' routes')
    print('Deleted '+str(Airport.query.delete())+' airports')
    print('Deleted '+str(County.query.delete())+' counties')
    print('Deleted '+str(State.query.delete())+' states')

    for entry in state_names:
        state = State(name=entry)
        db.session.add(state)



def populate_covid():
    print('Populating state and county data')
    print('retrieving data...')

    prev_cases = {}
    current_cases = {}

    county_results_old = json.loads(requests.get('https://disease.sh/v3/covid-19/nyt/counties?lastdays=14').text)

    #loop through two-week old COVID numbers
    for result in county_results_old:
        state_name = result['state']
        county_name = result['county']
        county = CountyTemplate(county_name, state_name)

        #check to see if we have looped through all the counties
        if(county in prev_cases):
            break

        prev_cases[county] = int(result['cases'])

    county_results_new = json.loads(requests.get('https://disease.sh/v3/covid-19/nyt/counties?lastdays=1').text)

    #loop through current COVID numbers
    for result in county_results_new:
        state_name = result['state']
        county_name = result['county']
        county = CountyTemplate(county_name, state_name)

        if(county in prev_cases):
            current_cases[county] = int(result['cases'])

    #make sure previous cases and current cases match up
    prev_cases = {entry: prev_cases[entry] for entry in current_cases}

    old_state_numbers = {key: 0 for key in state_names}
    cur_state_numbers = {key: 0 for key in state_names}

    print('updating database...')
    #update database with county values
    for entry in current_cases:
        #get relevant values
        state_name = entry.state_name
        county_name = entry.county_name
        old_cases = prev_cases[entry]
        cur_cases = current_cases[entry]
        new_cases = cur_cases - old_cases

        if(state_name in state_names):
            state = db.session.query(State).filter(func.lower(State.name) == state_name.lower()).first()

            county = County(
                        name = county_name.title(),
                        state = state,
                        cases_2_weeks_ago = old_cases,
                        total_cases = cur_cases,
                        new_cases = new_cases)

            db.session.add(county)

            old_state_numbers[state_name] += old_cases
            cur_state_numbers[state_name] += cur_cases

    #update database with state values
    for state_name in state_names:
        state = db.session.query(State).filter(func.lower(State.name) == state_name.lower()).first()
        state.cases_2_weeks_ago = old_state_numbers[state_name]
        state.total_cases = cur_state_numbers[state_name]
        state.new_cases = cur_state_numbers[state_name] - old_state_numbers[state_name]

if __name__ == '__main__':
    populate_states()
    populate_covid()
    db.session.commit()
    print("COVID numbers repopulated.")
