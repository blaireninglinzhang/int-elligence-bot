from flask import Flask, request, Response
from datetime import datetime
from flask_pymongo import PyMongo
from slackclient import SlackClient
import os, random, json
app = Flask(__name__)

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

app.config['MONGO_URI'] = "mongodb://slackathon:slackathon1@ds145951.mlab.com:45951/slackathon-bot"
app.config['MONGO_DBNAME'] = "slackathon-bot"
mongo = PyMongo(app)

CONFIRMATION_DIALOG = {
    "title": "Request a coffee",
    "submit_label": "Submit",
    "callback_id": "coffee_order_form",
    "elements": [
        {
            "label": "Coffee Type",
            "type": "select",
            "name": "meal_preferences",
            "placeholder": "Select a drink",
            "options": [
                {
                    "label": "Cappuccino",
                    "value": "cappuccino"
                },
                {
                    "label": "Latte",
                    "value": "latte"
                },
                {
                    "label": "Pour Over",
                    "value": "pour_over"
                },
                {
                    "label": "Cold Brew",
                    "value": "cold_brew"
                }
            ]
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


@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        # Slack sent a button press
        if request.content_type == "application/x-www-form-urlencoded":
            data = json.loads(request.form['payload'])
            print(data.keys())
            if data.get('callback_id', '') == "manual_add_text" and data.get("actions"):
                if data["actions"][0]["name"] == "manual_add_yes":
                    print("i am working")
                    slack_client.api_call(
                        "dialog.open",
                        trigger_id=data["trigger_id"],
                        dialog={
                            "title": "Request a coffee",
                            "submit_label": "Submit",
                            "callback_id":  "coffee_order_form",
                            "elements": [
                                {
                                    "label": "Coffee Type",
                                    "type": "text",
                                    "name": "meal_preferences",
                                    "placeholder": "Select a drink",
                                }
                            ]
                            }
                    )
                    return "hello"
                else:
                    return "SAD"
            else:
                return "ERROR"
        # Slack just sent an event
        elif request.content_type == "application/json":
            data = request.get_json()
            print(data)
            response = dict()
            if data.get('event', ''):
                event_type = data['event'].get('type', '')
                event_text = data['event'].get('text', '')[12:]
                # if the user uses the 'add' keyword
                print(event_type, event_text)
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

#  @app.route('/check-for-events', methods=['GET', 'POST'])
#  def check_for_events():
#      ## this is where logic for checking past events will go
#      if is_important_event():
#          # save to database
#          # prompt the workspace that something important happened
#          return "important"
#      return "not important"

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
