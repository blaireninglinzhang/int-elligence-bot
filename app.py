from flask import Flask, request, Response
from datetime import datetime
from flask_pymongo import PyMongo
from slackclient import SlackClient
import os, random, json

import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

def print_date_time():
    print("hello")

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=print_date_time,
    trigger=IntervalTrigger(seconds=60),
    id='printing_job',
    name='Print date and time every five seconds',
    replace_existing=True)
# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

app = Flask(__name__)

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slack_client_oauth = SlackClient(os.environ.get('SLACK_BOT_TOKEN_OAUTH'))

app.config['MONGO_URI'] = "mongodb://slackathon:slackathon1@ds145951.mlab.com:45951/slackathon-bot"
app.config['MONGO_DBNAME'] = "slackathon-bot"
mongo = PyMongo(app)

INTERNAL_CACHE = {}

COUNT_THRESHOLD = 2

DIALOG_SNIPPET = {
    "title": "Enter a milestone!",
    "submit_label": "Submit",
    "callback_id": "milestone_form",
    "elements": [
        {
            "label": "Milestone name: ",
            "type": "text",
            "name": "milestone_name",
            "placeholder": "We bought a chicken!",
        }
    ]
}

MANUAL_MILESTONE = {
    "text": "Hi there! Sounds like you're trying to create a new milestone!",
    "fallback": "Oh no, it failed.",
    "callback_id": "manual_add_text",
    "color": "#3AA3E3",
    "attachment_type": "default",
    "actions": [
        {
            "name": "manual_add_yes",
            "text": "Yes!",
            "type": "button",
            "value": "happy :grinning:",
        },
        {
            "name": "manual_add_yes",
            "text": "No",
            "style": "danger",
            "type": "button",
            "value": "sad :persevere:",
        }
    ]
}

SUGGESTED_MILESTONE = {
    "text": "Hi there! We noticed that this is an exciting time so we added a message as a milestone!",
    "fallback": "Oh no, it failed.",
    "callback_id": "manual_add_text",
    "color": "#3AA3E3",
    "attachment_type": "default"
}

@app.route('/add', methods=['GET'])
def add():
    return "ok"

@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        # Slack sent a button press
        if request.content_type == "application/x-www-form-urlencoded":
            data = json.loads(request.form['payload'])
            print(data.keys())
            print(data)
            if data.get('callback_id', '') == "milestone_form" and data.get('submission'):
                print(data['submission']['milestone_name'])
            if data.get('callback_id', '') == "manual_add_text" and data.get("actions"):
                if data["actions"][0]["name"] == "manual_add_yes":
                    slack_client.api_call(
                        "dialog.open",
                        trigger_id=data["trigger_id"],
                        dialog=DIALOG_SNIPPET
                    )
                else:
                    return "SAD"
            else:
                return "ERROR"
        # Slack just sent an event
        elif request.content_type == "application/json":
            data = request.get_json()
            response = dict()
            if data.get('event', ''):
                event_type = data['event'].get('type', '')
                event_text = data['event'].get('text', '')[12:]
                # if the user uses the 'add' keyword
                if event_type == "reaction_added":
                    message_time = data['event']['item']['ts']
                    if message_time in INTERNAL_CACHE:
                        INTERNAL_CACHE[data['event']['item']['ts']]['count'] += 1
                        if INTERNAL_CACHE[data['event']['item']['ts']]['count'] > COUNT_THRESHOLD and not INTERNAL_CACHE[message_time].get('stored'):
                            slack_client.api_call(
                                "chat.postMessage",
                                channel="CBVS7HV1C",
                                text="Good morning, int-elligence!",
                                attachments=[SUGGESTED_MILESTONE]
                            )
                            # do this after the user adds shit
                            messages = slack_client_oauth.api_call(
                                "channels.history",
                                channel="CBVS7HV1C",
                                latest=data['event']['item']['ts'],
                                count=1
                            )
                            INTERNAL_CACHE[message_time]['text'] = messages['messages'][0]['text']
                            mongo.db.channel_history.insert({message_time.replace(".","-"): INTERNAL_CACHE[message_time]})
                            INTERNAL_CACHE[message_time]['stored'] = True
                            print("wrote to database")
                    else:
                        INTERNAL_CACHE[message_time] = {}
                        INTERNAL_CACHE[message_time]['item'] = data['event']['item']
                        INTERNAL_CACHE[message_time]['count'] = 1
                    print(INTERNAL_CACHE[data['event']['item']['ts']]['count'])
                if event_type == "app_mention" and "add" in event_text:
                    slack_client.api_call(
                        "chat.postMessage",
                        channel="CBVS7HV1C",
                        text="Good morning, int-elligence!",
                        attachments=[MANUAL_MILESTONE]
                    )
                # testing query from the slack API
                if data.get('challenge', ''):
                    response['challenge'] = data['challenge']
                response = Response(response=json.dumps(response),
                                    status=200,
                                    mimetype='application/json')
                return response
    the_time = datetime.now().strftime("%A, %d %b %Y %l:%M %p")
    online_users = mongo.db.channel_history.count()
    print(online_users)
    return """
    <h1>Hello heroku</h1>
    <p>It is currently {time}.</p>
    <img src="http://loremflickr.com/600/400">
        """.format(time=the_time)

@app.route('/add-event', methods=['GET', 'POST'])
def add_event():
    # save to database
    # prompt the workspace that something important happened
    return "not important"

def is_important_event():
    # this is where code for reading history goes...
    return bool(random.getrandbits(1))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
