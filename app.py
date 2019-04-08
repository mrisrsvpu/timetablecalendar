from datetime import datetime, timedelta
from json import JSONDecodeError

import pytz
import requests
from flask import Flask, Response, abort
from icalendar import Calendar, Event

app = Flask(__name__)

TIMEZONE_NAME_OLSON = 'Asia/Yekaterinburg'
TIMEZONE = pytz.timezone(TIMEZONE_NAME_OLSON)

TIMEZONE_TIMEDELTA = TIMEZONE.utcoffset(datetime.utcnow())

TIMETABLE_API_HOST_NAME = 'timetable.mris.rsvpu.ru'


@app.route('/timetable/group/<c_id>')
def group_calendar(c_id):
    return generic_calendar(request_url='http://{}/group/{}'.format(TIMETABLE_API_HOST_NAME, c_id))


@app.route('/timetable/prep/<c_id>')
def prep_calendar(c_id):
    return generic_calendar(request_url='http://{}/prep/{}'.format(TIMETABLE_API_HOST_NAME, c_id))


@app.route('/timetable/aud/<c_id>')
def aud_calendar(c_id):
    return generic_calendar(request_url='http://{}/aud/{}'.format(TIMETABLE_API_HOST_NAME, c_id))


def generic_calendar(request_url):
    r = requests.get(request_url)
    try:
        data = r.json()
    except JSONDecodeError:
        return abort(400)
    cal = Calendar()
    cal.add('prodid', '-//RSVPU timetable calendar//')
    cal.add('version', '2.0')

    cal.add('calscale', 'GREGORIAN')
    #
    # tz_component = Timezone()
    # tz_component.add('tzid', TIMEZONE_NAME_OLSON)
    #
    # tz_daylight_component = TimezoneDaylight()
    # tz_daylight_component.add('tz')

    for d in data:
        if not d:
            continue
        if len(d['name']) < 3:
            continue
        date_start = datetime.strptime(d['data'] + 'T' + d['time'], '%d.%m.%YT%H:%M')
        date_start_aware = TIMEZONE.localize(date_start, is_dst=False)
        date_start_utc = date_start_aware.astimezone(pytz.utc)

        name = ' '.join([d['name'], d['class_room'], d['name_of_pedagog']])
        event = Event()
        event.add('summary', name)
        event.add('dtstart', date_start_utc)
        event.add('dtend', date_start_utc + timedelta(hours=1, minutes=35))
        event.add('dtstamp', datetime.utcnow())
        event.add('uid', str(abs(hash(str(name) + str(date_start_utc)))))
        cal.add_component(event)
    return Response(cal.to_ical(), mimetype='text/plain')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
