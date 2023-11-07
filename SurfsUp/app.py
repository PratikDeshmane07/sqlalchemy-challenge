from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# # reflect the tables
Base.prepare(autoload_with=engine)

# # Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# # Create our session (link) from Python to the DB
session = Session(engine)

# #################################################
# # Flask Setup
# #################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"<p>'start' and 'end' date should be in the format MMDDYYYY.</p>"

    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    last_data_point = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)

    # Query for the date and precipitation for the last year
    year_prcp = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago, Measurement.prcp != None).\
    order_by(Measurement.date).all()
    
    return jsonify(dict(year_prcp))

@app.route("/api/v1.0/stations")
def stations():
    session.query(Measurement.station).distinct().count()
    active_stations = session.query(Measurement.station,func.count(Measurement.station)).\
                               group_by(Measurement.station).\
                               order_by(func.count(Measurement.station).desc()).all()
                               
    return jsonify(dict(active_stations))
                           
@app.route("/api/v1.0/tobs")
def tobs():
    
    year_ago = dt.date(2017,8,23) - dt.timedelta(days= 365)
    year_temp = session.query(Measurement.tobs).\
        filter(Measurement.date >= year_ago, Measurement.station == 'USC00519281').\
        order_by(Measurement.tobs).all()

    yr_temp = []
    for y_t in year_temp:
        yrtemp = {}
        yrtemp["tobs"] = y_t.tobs
        yr_temp.append(yrtemp)

    return jsonify(yr_temp)

def calc_start_temps(start_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()

@app.route("/api/v1.0/<start>")
    
def start_date(start):
    calc_start_temp = calc_start_temps(start)
    t_temp= list(np.ravel(calc_start_temp))

    t_min = t_temp[0]
    t_max = t_temp[2]
    t_avg = t_temp[1]
    t_dict = {'Minimum temperature': t_min, 'Maximum temperature': t_max, 'Avg temperature': t_avg}

    return jsonify(t_dict)

def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    Args:
    start_date (string): A date string in the format %Y-%m-%d
    end_date (string): A date string in the format %Y-%m-%d
    Returns:
    TMIN, TAVE, and TMAX
    """
    start = dt.datetime.strptime(start_date, "%m%d%Y")
    end = dt.datetime.strptime(end_date, "%m%d%Y")
    
    return session.query(func.min(Measurement.tobs), \
                         func.avg(Measurement.tobs), \
                         func.max(Measurement.tobs)).\
                         filter(Measurement.date >= start).\
                         filter(Measurement.date <= end).all()


@app.route("/api/v1.0/<start>/<end>")

def start_end_date(start, end):
    
    calc_temp = calc_temps(start, end)
    ta_temp= list(np.ravel(calc_temp))
    tmin = ta_temp[0]
    tmax = ta_temp[2]
    temp_avg = ta_temp[1]
    
    temp_dict = { 'Minimum temperature': tmin, 'Maximum temperature': tmax, 'Avg temperature': temp_avg}

    return jsonify(temp_dict)
    



if __name__ == '__main__':
    app.run(debug=True)