import os
import sentry_sdk
import requests

from bottle import Bottle, request, response
from sentry_sdk.integrations.bottle import BottleIntegration

sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"), # SENTRY_DSN в окружении Heroku или локально
        integrations=[BottleIntegration()])

auth_token = {
    'Authorization': os.environ.get("SENTRY_TOKEN") # SENTRY_TOKEN в окружении Heroku или локально
}
events_url = 'https://sentry.io/api/0/projects/ivan-revyakin/skillfactory-d2/events/'
event_url = events_url + "{}/"

app = Bottle()

@app.route("/")
@app.route("/success")
def success():
    return "success\n"

@app.route("/fail")
def one_message():
    raise RuntimeError("fail")
    return "fail\n"

@app.route("/logs")
@app.route("/logs/")
def get_logs():
    '''
    Ототбражаем список событий в sentry.io
    '''
    resp = requests.get(events_url, headers=auth_token)
    if not resp.ok:
        return resp.text
    jresp = resp.json()
    html = ""
    for event in jresp:
        html = html + "<a href=/logs/{e}>{e}</a> {d}<br>".format(e=event['eventID'], d=event['dateCreated'])
    return html

@app.route("/logs/<eid>")
def get_event(eid):
    '''
    Ототбражаем одно событие в виде JSON
    '''
    resp = requests.get(event_url.format(eid), headers=auth_token)
    if not resp.ok:
        return resp.text
    response.content_type = 'application/json'
    return resp.json()

if os.environ.get("APP_LOCATION") == "heroku":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        server="gunicorn",
        workers=3,
    )
else:
    app.run(host="localhost", port=8080, debug=True)
