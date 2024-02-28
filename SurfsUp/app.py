# Import the dependencies.
#import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#save a value, year_earlier which will be used in multiple queries
year_earlier = dt.date(2017, 8, 23) - dt.timedelta(days=365)

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
measures = Base.classes.measurement
stations = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
#home page
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end>"
    )

#precipitation results page: returns the precipitation amounts for the most recent year
@app.route("/api/v1.0/precipitation")
def precip():
    # Query the date and precipitation data
    #TODO can I get the most recent year's data without hardcoding?
    results = session.query(measures.date, measures.prcp).filter(measures.date >= year_earlier).all()
    
    # Close Session
    session.close()
    weather_dict = {date: rainfall for date, rainfall in results}
   
    # Convert the data frame to json object and return
    return jsonify(weather_dict)

#station results page: returns the station information
@app.route("/api/v1.0/stations")
def station_display():
    results_s = session.query(stations.id, stations.station, stations.name, stations.latitude, stations.longitude, stations.elevation).all()
    session.close()
    station_dict = {id: (station, name, latitude, longitude, elevation) for id, station, name, latitude, longitude, elevation in results_s}

    # convert the data fram to json object and return
    return jsonify(station_dict)

#temperature observations page: returns the temperatures
@app.route("/api/v1.0/tobs")
def tobs_display():
    station_activity = session.query(measures.station, func.count(measures.station)).group_by(measures.station).order_by(func.count(measures.station).desc()).all()
    # Close Session
    session.close()
    most_active = station_activity[0][0]

    temps = session.query(measures.date, measures.tobs).\
    filter(measures.date >= year_earlier).\
    filter(measures.station == most_active).\
    all()
    temps = {date: tobs for date, tobs in temps} 
    return jsonify(temps)

@app.route("/api/v1.0/<start>")
def stats_start(start):
    result = session.query(func.min(measures.tobs)).\
    filter(measures.date >= start).all()
    # Close Session
    session.close()
    result_l = [result[0]]
    return jsonify(result_l)

if __name__ == '__main__':
    app.run(debug=True)