from decimal import Decimal
from flask import Flask
from flask import request
import psycopg2

from connection import config

DATABASE_CONFIG = config()

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, World!"

@app.route("/temperature")
def get_temperature():
    with psycopg2.connect(**DATABASE_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM state;")
            states = cursor.fetchall()
            for state in states:
                print(state)
    return f"Temperature is {42}"

@app.route("/state")
def set_state():
    temperature = Decimal(request.args["temperature"])
    humidity = Decimal(request.args["humidity"])
    
    with psycopg2.connect(**DATABASE_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO state(temperature, humidity, datetime)
                VALUES(%s, %s, current_timestamp)""", 
                (temperature, humidity)
            )

    return f"Temperature {temperature} and humidity {humidity} recorded."

@app.route("/humidity")
def get_humidity():
    return f"Humidity is {45}"
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=57633, debug=True)