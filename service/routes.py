from decimal import Decimal
from flask import Blueprint
from flask import Flask
from flask import make_response
from flask import jsonify
from flask import request
from flask import render_template
from flask_login import login_required
from flask_login import current_user
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2

from service.database_connection import config
from service import db
from service import login_manager

from .models import User

DATABASE_CONFIG = config()

main = Blueprint("main", __name__)
auth = HTTPBasicAuth()

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


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(email = username).first()
    if not user or not check_password_hash(user.password, password):
        return False
    return True
    

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
@auth.login_required
def get_humidity():
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
