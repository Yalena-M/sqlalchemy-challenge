# Import the dependencies
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt  

#################################################
# Database Setup
#################################################

####API SQLite Connection & Landing Page
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

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
    return (
        f"Welcome to the Climate Analysis API!<br>"
        f"Available Routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/&lt;start&gt;<br>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )


###API Static Routes
@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    start_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.prcp).filter(
        Measurement.date >= start_date.strftime('%Y-%m-%d')
    ).all()

    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.station).all()
    stations = [station[0] for station in results]
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def tobs():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    start_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d") - dt.timedelta(days=365)
    
    most_active_station = session.query(
        Measurement.station,
        func.count(Measurement.station).label('count')
    ).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    
    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station,
        Measurement.date >= start_date.strftime('%Y-%m-%d')
    ).all()
    
    tobs_data = {date: tobs for date, tobs in results}
    
    return jsonify(tobs_data)

###API Dynamic Route
@app.route("/api/v1.0/<start>")
def start(start):
    results = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp'),
        func.max(Measurement.tobs).label('max_temp')
    ).filter(Measurement.date >= start).all()
    
    temp_stats = []
    for min_temp, avg_temp, max_temp in results:
        temp_stats.append({
            'TMIN': min_temp,
            'TAVG': avg_temp,
            'TMAX': max_temp
        })
    
    return jsonify(temp_stats)

@app.route("/api/v1.0/<start>/<end>")
def end(start, end):
    results = session.query(
        func.min(Measurement.tobs).label('min_temp'),
        func.avg(Measurement.tobs).label('avg_temp'),
        func.max(Measurement.tobs).label('max_temp')
    ).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    temp_stats = []
    for min_temp, avg_temp, max_temp in results:
        temp_stats.append({
            'TMIN': min_temp,
            'TAVG': avg_temp,
            'TMAX': max_temp
        })
    
    return jsonify(temp_stats)

if __name__ == "__main__":
    app.run(debug=True)
