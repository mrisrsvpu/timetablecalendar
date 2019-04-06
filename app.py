from datetime import datetime, timedelta
import requests
import pytz as pytz
from flask import Flask
from icalendar import Calendar, Event

app = Flask(__name__)

V_GROUP = 2549

REQUEST_TEMPLATE = 'http://timetable.mris.mikhailche.ru/group/{}'

TIMEZONE = pytz.timezone('Asia/Yekaterinburg')


@app.route('/')
def hello_world():
    r = requests.get(REQUEST_TEMPLATE.format(V_GROUP))
    data = r.json()
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')
    for d in data:
        if not d:
            continue
        if len(d['name']) < 3:
            continue
        date_start = datetime.strptime(d['data']+'T'+d['time'], '%d.%m.%YT%H:%M')
        date_start.replace(tzinfo=TIMEZONE)

        name = ' '.join([d['name'], d['class_room'], d['name_of_pedagog']])

        event = Event()
        event.add('summary', name)
        event.add('dtstart', date_start)
        event.add('dtend', date_start + timedelta(hours=1, minutes=35))
        event.add('dtstamp', datetime.utcnow())
        cal.add_component(event)
    return cal.to_ical()


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
