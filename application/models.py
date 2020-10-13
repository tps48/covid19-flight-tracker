from app import db
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship


class State(db.Model):
    __tablename__ = 'state'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(length=20))
    cases_2_weeks_ago = db.Column(db.Integer, default=0)
    total_cases = db.Column(db.Integer, default=0)
    new_cases = db.Column(db.Integer, default=0)

    counties = relationship('County', back_populates='state')

    def __repr__(self):
        return '{}: {} new cases'.format(self.name, self.new_cases)


class County(db.Model):
    __tablename__ = 'county'

    id = db.Column(db.Integer, primary_key = True)
    state_id = db.Column(db.Integer, ForeignKey('state.id'))
    state = relationship('State', back_populates = 'counties')  
    name = db.Column(db.String(length=50))
    cases_2_weeks_ago = db.Column(db.Integer, default=0)
    total_cases = db.Column(db.Integer, default=0)
    new_cases = db.Column(db.Integer, default=0)

    airports = relationship('Airport', back_populates='county')

    def __repr__(self):
        return '{}: {} new cases'.format(self.name, self.new_cases)

class Airport(db.Model):
    __tablename__ = 'airport'

    id = db.Column(db.Integer, primary_key = True)
    icao24 = db.Column(db.String(length=4))
    county_id = db.Column(db.Integer, ForeignKey('county.id'))
    county = relationship('County', back_populates = 'airports')
    code = db.Column(db.String(length=3))
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())

    departed_flights = relationship('Flight', back_populates='departing_airport', foreign_keys='Flight.departing_airport_id')
    arriving_flights = relationship('Flight', back_populates='arriving_airport', foreign_keys='Flight.arriving_airport_id')
    outgoing_routes = relationship('Route', back_populates='source_airport', foreign_keys='Route.source_airport_id')
    incoming_routes = relationship('Route', back_populates='dest_airport', foreign_keys='Route.dest_airport_id')



class Flight(db.Model):
    __tablename__ = 'flight'

    id = db.Column(db.Integer, primary_key = True)
    flight_number = db.Column(db.String(length=20))

    departing_airport_id = db.Column(db.Integer, ForeignKey('airport.id'))
    departing_airport = relationship('Airport', back_populates = 'departed_flights', foreign_keys=[departing_airport_id])

    arriving_airport_id = db.Column(db.Integer, ForeignKey('airport.id'))
    arriving_airport = relationship('Airport', back_populates = 'arriving_flights', foreign_keys=[arriving_airport_id])

    departure_time = db.Column(db.TIMESTAMP())
    expected_arrival_time = db.Column(db.TIMESTAMP())
    latitude = db.Column(db.Float())
    longitude = db.Column(db.Float())
    on_ground = db.Column(db.Boolean())
    true_tracks = db.Column(db.Float())
    last_updated = db.Column(db.TIMESTAMP())

class Route(db.Model):
    __tablename__ = 'route'

    id = db.Column(db.Integer, primary_key = True)

    source_airport_id = db.Column(db.Integer, ForeignKey('airport.id'))
    source_airport = relationship('Airport', back_populates = 'outgoing_routes', foreign_keys=[source_airport_id])

    dest_airport_id = db.Column(db.Integer, ForeignKey('airport.id'))
    dest_airport = relationship('Airport', back_populates = 'incoming_routes', foreign_keys=[dest_airport_id])


