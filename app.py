from flask import Flask
from flask_apscheduler import APScheduler
from NJTBusXMLScraper import parse_njt
import pyodbc, sqlalchemy

app = Flask(__name__)
schedule = APScheduler()
schedule.start()


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@schedule.task('interval',minutes=1)
def parseNJT():
    print(parse_njt())