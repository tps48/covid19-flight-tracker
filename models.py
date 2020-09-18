from app import db
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

class State(db.Model):
    __tablename__ = 'state'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(length=20))
    abbreviation = db.Column(db.String(length=2))
    cases_2_weeks_ago = db.Column(db.Integer, default=0)
    total_cases = db.Column(db.Integer, default=0)
    new_cases = db.Column(db.Integer, default=0)

    counties = relationship('County')


class County(db.Model):
    __tablename__ = 'county'

    id = db.Column(db.Integer, primary_key = True)
    state_id = db.Column(db.Integer, ForeignKey('state.id'))
    name = db.Column(db.String(length=20))
    cases_2_weeks_ago = db.Column(db.Integer, default=0)
    total_cases = db.Column(db.Integer, default=0)
    new_cases = db.Column(db.Integer, default=0)

    airports = relationship('Airport')


class Airport(db.Model):
    __tablename__ = 'airport'

    id = db.Column(db.Integer, primary_key = True)
    icao24 = db.Column(db.String(length=4))
    county_id = db.Column(db.Integer, ForeignKey('county.id'))
    code = db.Column(db.String(length=3))


class Flight(db.Model):
    __tablename__ = 'flight'

    id = db.Column(db.Integer, primary_key = True)
    flight_number = db.Column(db.String(length=20))
    departing_airport_id = db.Column(db.Integer, ForeignKey('airport.id'))
    arriving_airport_id = db.Column(db.Integer, ForeignKey('airport.id'))
    departure_time = db.Column(db.TIMESTAMP())
    expected_arrival_time = db.Column(db.TIMESTAMP())
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())
    delayed = db.Column(db.Boolean())
    en_route = db.Column(db.Boolean())
    last_updated = db.Column(db.TIMESTAMP())

