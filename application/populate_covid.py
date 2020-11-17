import requests
import json
import sys
from app import db
from models import Flight, Airport, County, State

#THIS IS DEPRECATED DO NOT RUN THIS
def DO_NOT_RUN():
    state_result = json.loads(requests.get('https://corona.lmao.ninja/v2/historical/usacounties').text)
    excluded_states = ['diamond princess', 'grand princess', 'american samoa', 'northern mariana islands']
    state_result = [elem for elem in state_result if elem not in excluded_states]

    # delete existing entries
    print('Deleted '+str(County.query.delete())+' counties')
    print('Deleted '+str(State.query.delete())+' states')

    #repopulate database
    for state_name in state_result:
        result = json.loads(requests.get('https://corona.lmao.ninja/v2/historical/usacounties/' + state_name +'?lastdays=14').text)
            
        state = State(name=state_name.title())
        print('State: ' + state.name)

        sum_2_week_cases = 0
        sum_current_cases = 0

        try:
            for county in result:
                name = county['county']
                if name is not None and 'out of' not in name and name != 'unassigned':
                    case_list = list(county['timeline']['cases'].values())
                    cases_2_weeks_ago = case_list[0]
                    current_cases = case_list[-1]
                    new_cases = current_cases - cases_2_weeks_ago;

                    sum_2_week_cases += cases_2_weeks_ago
                    sum_current_cases += current_cases

                    print(name)

                    county = County(
                        name = name.title(),
                        state = state,
                        cases_2_weeks_ago = cases_2_weeks_ago,
                        total_cases = current_cases,
                        new_cases = new_cases)

                    db.session.add(county)

        except Exception as e:
            print('ERROR: Unable to add counties for the state ' + state_name + ' ' + str(e))

        state.cases_2_weeks_ago = sum_2_week_cases
        state.total_cases = sum_current_cases
        state.new_cases = sum_current_cases - sum_2_week_cases
        db.session.commit()
    


#excluded_counties = ['out of dc', None]
#result = json.loads(requests.get('https://corona.lmao.ninja/v2/historical/usacounties/district of columbia?lastdays=14').text)
#first = list(result[0]['timeline']['cases'].values())
#print(result)

#for county in result:
#    if county['county'] not in excluded_counties:
