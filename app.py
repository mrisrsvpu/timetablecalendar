from datetime import datetime

import pytz as pytz
from flask import Flask
from icalendar import Calendar, Event

app = Flask(__name__)


@app.route('/')
def hello_world():
    cal = Calendar()
    event = Event()
    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')
    event.add('summary', 'Python meeting about calendaring')
    event.add('dtstart', datetime(2005, 4, 4, 8, 0, 0, tzinfo=pytz.utc))
    event.add('dtend', datetime(2005, 4, 4, 10, 0, 0, tzinfo=pytz.utc))
    event.add('dtstamp', datetime(2005, 4, 4, 0, 10, 0, tzinfo=pytz.utc))
    return cal.to_ical()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
