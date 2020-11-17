#!/usr/bin/env bash
python application/populate_covid_new.py
python application/update_state_geo.py
python application/update_county_geo.py
python application/populate_airports.py
python application/populate_routes.py