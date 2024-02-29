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
    #Query the station data
    results_s = session.query(stations.id, stations.station, stations.name, stations.latitude, stations.longitude, stations.elevation).all()
    #close the session
    session.close()
    #use a dictionary comprehension to put results into a dictionary which can be jsonified
    station_dict = {id: (station, name, latitude, longitude, elevation) for id, station, name, latitude, longitude, elevation in results_s}
    # convert the data fram to json object and return
    return jsonify(station_dict)

#temperature observations page: returns the temperatures from the most active station in the previous year
@app.route("/api/v1.0/tobs")
def tobs_display():
    #Query to find the most active station.  Note: This station is the most active for all time.
    #It is not necessarily the most active station when considering only the past year.
    station_activity = session.query(measures.station, func.count(measures.station)).\
        group_by(measures.station).order_by(func.count(measures.station).desc()).all()
    most_active = station_activity[0][0]

    #Query to find the previously slected station's temperature data for the last year.
    temps = session.query(measures.date, measures.tobs).\
    filter(measures.date >= year_earlier).\
    filter(measures.station == most_active).\
    all()

    # Close Session
    session.close()
    temps = {date: tobs for date, tobs in temps} 
    return jsonify(temps)

#temperature statistics page:  returns min, avg and max temperature values from a specified start date until the most recent data
#written with assistance from UofO/edX bootcamp's "Xpert Learning Assistant" AI
@app.route("/api/v1.0/<start>")
def stats_start(start):
    #query the desired information
    result = session.query(func.min(measures.tobs), func.avg(measures.tobs), func.max(measures.tobs)).\
        filter(measures.date >= start).all()
    
    # Extract the values from the result
    min_temp = result[0][0] 
    avg_temp = result[0][1]
    max_temp = result[0][2]
    
    # Close Session
    session.close()
    
    #return the jsonified values
    return jsonify({"minimum temperature": min_temp,
                    'avgerage temperature': avg_temp,
                    "maximum temperature:": max_temp})

@app.route("/api/v1.0/<start>/<end>")
def stats_start_end(start, end):
    #query the desired information
    result = session.query(func.min(measures.tobs), func.avg(measures.tobs), func.max(measures.tobs)).\
        filter(measures.date >= start).filter(measures.date <= end)

    # Extract the values from the result
    min_temp = result[0][0] 
    avg_temp = result[0][1]
    max_temp = result[0][2]
    
    # Close Session
    session.close()
    
    #return the jsonified values
    return jsonify({'minimum temperature': min_temp,
                    'avgerage temperature': avg_temp,
                    'maximum temperature:': max_temp})
if __name__ == '__main__':
    app.run(debug=True)