from app import db
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from models import Airport
from geojson import Point, Feature, FeatureCollection, dump
from sqlalchemy import func

airportQuery = db.session.query(Airport).all()
features = []

for airport in airportQuery:
    point = Point((float(airport.longitude), float(airport.latitude)))
    
    features.append(Feature(geometry=point, properties={"name": airport.code}))

feature_collection = FeatureCollection(features)

with open('./json/airportData.geojson', 'w') as f:
    dump(feature_collection, f)
    
