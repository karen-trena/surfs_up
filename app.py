import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
engine = create_engine("sqlite:///hawaii.sqlite") #The create_engine() allows us to access and query our SQLite database file

Base = automap_base() #Reflect the database into our classes.
Base.prepare(engine, reflect=True) #Now,we're going to reflect our tables

# We'll create a variable for each of the classes so that we can reference them later
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine) #create a session link from Python to our database with the following code


app = Flask(__name__) #This will create a Flask application called "app."
#All of your routes should go after the app = Flask(__name__) line of code.


@app.route("/") #define the welcome route

def welcome():
    return(
    '''
    Welcome to the Climate Analysis API!
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/temp/start/end
    ''')

@app.route("/api/v1.0/precipitation")
def precipitation():
   prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365) #calculates the date one year ago from the most recent date in the database
   precipitation = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= prev_year).all()
    #get the date and precipitation for the previous year
    #Notice the .\ in the first line of our query? This is used to signify that we want our query to continue on the next line.
   precip = {date: prcp for date, prcp in precipitation} #we'll create a dictionary with the date as the key and the precipitation as the value.
   return jsonify(precip) #Jsonify() is a function that converts the dictionary to a JSON file.

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))  #We want to start by unraveling our results into a one-dimensional array.
    #To convert the results to a list, 
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs") #The goal is to return the temperature observations for the previous year.
def temp_monthly():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).\
      filter(Measurement.station == 'USC00519281').\
      filter(Measurement.date >= prev_year).all()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

@app.route("/api/v1.0/temp/<start>") #Our last route will be to report on the minimum, average, and maximum temperatures
@app.route("/api/v1.0/temp/<start>/<end>")

def stats(start=None, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)] #We'll start by just creating a list called sel

    if not end:  #Since we need to determine the starting and ending date, add an if-not statement to our code
        results = session.query(*sel).\
            filter(Measurement.date >= start).all()
            # the asterisk is used to indicate there will be multiple results for our query: minimum, average, and maximum temperatures.
        temps = list(np.ravel(results))
        return jsonify(temps)

    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    temps = list(np.ravel(results))
    return jsonify(temps)