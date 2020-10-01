import requests
import json
import sys
import os
from app import db
from models import Flight, Airport, County, State
from sqlalchemy import func

def update_covid_db():
    print('starting...')
    state_result = json.loads(requests.get('https://corona.lmao.ninja/v2/historical/usacounties').text)
    excluded_states = ['diamond princess', 'grand princess', 'american samoa', 'northern mariana islands']
    state_result = [elem for elem in state_result if elem not in excluded_states]
    print(state_result)

    #load the mapbox tileset
    script_dir = os.path.dirname(__file__)
    f = open(script_dir + '/json/stateData.geojson', 'r')
    contents = f.read()
    f.close()
    mapbox_data = json.loads(contents)
    mapbox_dict = mapbox_data['features']

    #count number counties updated
    count = 0

    for state_name in state_result:
        current_state = db.session.query(State).filter(func.lower(State.name) == state_name.lower()).all()

        if len(current_state) > 0:  # make sure there is a match in the db

            current_state = current_state[0]
            print('State: ' + current_state.name)

            # get county numbers
            result = json.loads(requests.get('https://corona.lmao.ninja/v2/historical/usacounties/' + state_name +'?lastdays=14').text)

            sum_2_week_cases = 0
            sum_current_cases = 0

            # update counties
            
            for county in result:

                name = county['county']
                if name is not None and 'out of' not in name and name != 'unassigned':
                    case_list = list(county['timeline']['cases'].values())
                    cases_2_weeks_ago = case_list[0]
                    current_cases = case_list[-1]
                    new_cases = current_cases - cases_2_weeks_ago;

                    sum_2_week_cases += cases_2_weeks_ago
                    sum_current_cases += current_cases

                    current_county = db.session.query(County).filter(County.state == current_state).filter(County.name == name.title())[0]

                    if current_county.cases_2_weeks_ago != cases_2_weeks_ago or current_county.total_cases != current_cases:
                        count += 1
                        # update county numbers
                        current_county.cases_2_weeks_ago = cases_2_weeks_ago
                        current_county.total_cases = current_cases
                        current_county.new_cases = new_cases

            # update state numbers
            current_state.cases_2_weeks_ago = sum_2_week_cases
            current_state.total_cases = sum_current_cases
            current_state.new_cases = sum_current_cases - sum_2_week_cases

            db.session.commit()

            # update mapbox tile data
            state_dict = list(filter(lambda item: item['properties']['name'].lower() == state_name, mapbox_dict))[0]
            state_dict['properties']['cases'] = sum_current_cases - sum_2_week_cases

    print('Updated {} counties'.format(count))

    # write updated data to file
    with open(script_dir + '/json/stateData.geojson', 'w') as outfile:
        json.dump(mapbox_data, outfile)

if __name__ == '__main__':
    update_covid_db()