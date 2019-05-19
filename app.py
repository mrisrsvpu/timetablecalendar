import logging
from datetime import datetime, timedelta
from json import JSONDecodeError

import pytz
import requests
import sentry_sdk
from flask import Flask, Response, abort
from icalendar import Calendar, Event
from sentry_sdk.integrations.flask import FlaskIntegration

log = logging.getLogger(__name__)

try:
    sentry_sdk.init(
        dsn="https://3e7faf13b25a4104aa81c6e0b0cfbbd5:488995de1d394590bcf2077b4ec7489a@sentry-prod.mris.rsvpu.ru/2",
        integrations=[FlaskIntegration()]
    )
except:
    log.exception('Invalid sentry configuration')

app = Flask(__name__)

TIMEZONE_NAME_OLSON = 'Asia/Yekaterinburg'
TIMEZONE = pytz.timezone(TIMEZONE_NAME_OLSON)

TIMEZONE_TIMEDELTA = TIMEZONE.utcoffset(datetime.utcnow())

TIMETABLE_API_HOST_NAME = 'rsvpu.ru'


@app.route('/timetable/group/<c_id>')
def group_calendar(c_id):
    return generic_calendar(
        request_url='http://{}/contents/api/rasp.php?v_gru={}'.format(
            TIMETABLE_API_HOST_NAME, c_id
        )
    )


@app.route('/timetable/prep/<c_id>')
def prep_calendar(c_id):
    return generic_calendar(
        request_url='http://{}/contents/api/rasp.php?v_prep={}'.format(
            TIMETABLE_API_HOST_NAME, c_id
        )
    )


@app.route('/timetable/aud/<c_id>')
def aud_calendar(c_id):
    return generic_calendar(
        request_url='http://{}/contents/api/rasp.php?v_aud={}'.format(
            TIMETABLE_API_HOST_NAME, c_id
        )
    )


def generic_calendar(request_url):
    r = requests.get(request_url, verify=False)
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
        date_start = datetime.strptime(d['date'] + 'T' + d['time'], '%d.%m.%YT%H:%M')
        date_start_aware = TIMEZONE.localize(date_start, is_dst=False)
        date_start_utc = date_start_aware.astimezone(pytz.utc)

        name = d['timetable'].strip()
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
