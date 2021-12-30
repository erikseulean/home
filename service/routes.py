from decimal import Decimal
from flask import Blueprint
from flask import Flask
from flask import make_response
from flask import jsonify
from flask import request
from flask import render_template
from flask_login import login_required
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
import psycopg2

from service.database_connection import config
from service import db
from service import login_manager

DATABASE_CONFIG = config()

main = Blueprint("main", __name__)


def respond(fullfilment):
    return make_response(jsonify({
        "payload": {
            "google": {
            "expectUserResponse": True,
            "richResponse": {
                "items": [
                {
                    "simpleResponse": {
                    "textToSpeech": fullfilment
                    }
                }
                ]
            }
            }
        }
        })
    )
    


@main.route("/")
@login_required
def home():
    with psycopg2.connect(**DATABASE_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT temperature, humidity, datetime 
                FROM state order by datetime desc LIMIT 1;"""
            )
            state = cursor.fetchone()
    return render_template("home.html", temperature=state[0], humidity=state[1], dt=state[2].strftime("%c"))


@main.route("/temperature")
def get_temperature():
    with psycopg2.connect(**DATABASE_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM state;")
            states = cursor.fetchall()
            for state in states:
                print(state)
    return f"Temperature is {42}"


@main.route("/state")
def set_state():
    temperature = Decimal(request.args["temperature"])
    humidity = Decimal(request.args["humidity"])

    with psycopg2.connect(**DATABASE_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO state(temperature, humidity, datetime)
                VALUES(%s, %s, current_timestamp)""",
                (temperature, humidity),
            )

    return f"Temperature {temperature} and humidity {humidity} recorded."


@main.route("/humidity", methods=["POST"])
def get_humidity():
    if not current_user.is_authenticated:
        return False
    with psycopg2.connect(**DATABASE_CONFIG) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT humidity, datetime 
                FROM state order by datetime desc LIMIT 1;"""
            )
            state = cursor.fetchone()
    return respond(f"Humidity is {state[0]}% at {state[1].strftime('%c')}.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=57633, debug=True)
