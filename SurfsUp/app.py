# Import the dependencies.
#import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)
# reflect the tables
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
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations"
        f"/api/v1.0/tobs"
        f"/api/v1.0/<start>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
     # Create our session (link) from Python to the DB
    session = Session(engine)   
    # Query the date and precipitation data
    # Calculate the date one year from the last date in data set.
    
    #TODO can I get the most recent year's data without hardcoding?
    year_earlier = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(measures.date, measures.prcp).filter(measures.date >= year_earlier).all()

    # Close Session
    session.close()
    
    
    #weather_df = pd.DataFrame(precip, columns = ['Date', 'Precipitation'])
    #weather_df.set_index('Date', inplace = True)
    # Convert the data frame to json object
    json = weather_df.to_json()
    return json

if __name__ == '__main__':
    app.run(debug=True)