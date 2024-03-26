# Import the dependencies.
%matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)
class_names = Base.classes.keys()
print(class_names)

Measurement = Base.classes.measurement
Station = Base.classes.station

SM = sessionmaker(bind=engine)
S = Session()

# Exploratory Precipitation Analysis

mrd = session.query(func.max(Measurement.date)).scalar()
print(mrd)

ld = session.query(func.max(Measurement.date)).scalar()
oya = (pd.to_datetime(ld) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
results = session.query(Measurement.date, Measurement.prcp)\
                  .filter(Measurement.date >= oya)\
                  .order_by(Measurement.date).all()
df = pd.DataFrame(results, columns=['Date', 'Precipitation'])
df = df.sort_values(by='Date')
df.plot(x='Date', y='Precipitation', figsize=(10, 6))
plt.xlabel("Date")
plt.ylabel("Precipitation (inches)")
plt.title("Precipitation Over the Last 12 Months")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

stats = df['Precipitation'].describe()
display(stats)

# Exploratory Station Analysis

stations = session.query(func.count(Station.station)).scalar()
print("Total number of stations:", stations)

astations = session.query(Measurement.station, func.count(Measurement.station))\
                         .group_by(Measurement.station)\
                         .order_by(func.count(Measurement.station).desc())\
                         .all()

for station, count in astations:
    print(f"Station: {station}, Count: {count}")

    mastation = astations[0][0]

temps = session.query(func.min(Measurement.tobs),
                                  func.max(Measurement.tobs),
                                  func.avg(Measurement.tobs))\
                           .filter(Measurement.station == mastation)\
                           .all()

print(f"Most Active Station: {mastation}")
print(f"Lowest Temperature: {temps[0][0]}")
print(f"Highest Temperature: {temps[0][1]}")
print(f"Average Temperature: {temps[0][2]}")

tdata = session.query(Measurement.tobs)\
                          .filter(Measurement.station == mastation)\
                          .filter(Measurement.date >= oya)\
                          .all()

temp = [temp[0] for temp in tdata]

plt.hist(temp, bins=12)
plt.xlabel('Temperature (°F)')
plt.ylabel('Frequency')
plt.title('Temperature Observation Data (Last 12 Months)')
plt.legend(['tobs'], loc='upper right')
plt.tight_layout()
plt.show()

# Close Session
session.close()

#################################################
# Flask Setup
#################################################

from flask import Flask

app = Flask(__name__)

# Define a route
@app.route('/')
def hello_world():
    return 'Hello, World!'

# Run the application
if __name__ == '__main__':
    app.run(debug=True)





#################################################
# Flask Routes
#################################################
@app.route('/api/v1.0/precipitation')
def precipitation():
    results = session.query(Measurement.date, Measurement.prcp)\
                    .filter(Measurement.date >= oya)\
                    .order_by(Measurement.date).all()

    precipitation_data = []
    for date, prcp in results:
        precipitation_data.append({'date': date, 'precipitation': prcp})

    return jsonify(precipitation_data)


@app.route('/api/v1.0/stations')
def stations():
    results = session.query(Station.station, Station.name).all()

    station_data = []
    for station, name in results:
        station_data.append({'station': station, 'name': name})

    return jsonify(station_data)


@app.route('/api/v1.0/tobs')
def tobs():
    results = session.query(Measurement.date, Measurement.tobs)\
                    .filter(Measurement.date >= oya)\
                    .order_by(Measurement.date).all()

    tobs_data = []
    for date, tobs in results:
        tobs_data.append({'date': date, 'tobs': tobs})

    return jsonify(tobs_data)


@app.route('/api/v1.0/<start>')
def start_date(start):
    results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs))\
                    .filter(Measurement.date >= start)\
                    .all()

    temperature_data = {
        "start_date": start,
        "min_temperature": results[0][0],
        "max_temperature": results[0][1],
        "avg_temperature": results[0][2]
    }

    return jsonify(temperature_data)


@app.route('/api/v1.0/<start>/<end>')
def start_end_date(start, end):
    results = session.query(func.min(Measurement.tobs),
                            func.max(Measurement.tobs),
                            func.avg(Measurement.tobs))\
                    .filter(Measurement.date >= start)\
                    .filter(Measurement.date <= end)\
                    .all()

    temperature_data = {
        "start_date": start,
        "end_date": end,
        "min_temperature": results[0][0],
        "max_temperature": results[0][1],
        "avg_temperature": results[0][2]
    }

    return jsonify(temperature_data)
