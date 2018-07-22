from flask import Flask, request, Response
from datetime import datetime
from flask_pymongo import PyMongo
from slackclient import SlackClient
import os, random, json

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
    "text": "Hi there! We noticed that this is an exciting time so we added this message to milestones! \n View all milestones by typing `@Memory-Bot popular`",
    "fallback": "Oh no, it failed.",
    "callback_id": "manual_add_text",
    "color": "#3AA3E3",
    "attachment_type": "default"
}

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
                mongo.db.channel_history.insert({'text': data['submission']['milestone_name']})
                response = Response(response={},
                    status=200,
                    mimetype='application/json')
                return response
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
                        print("increasing count")
                        INTERNAL_CACHE[data['event']['item']['ts']]['count'] += 1
                        if INTERNAL_CACHE[message_time]['count'] > COUNT_THRESHOLD and not INTERNAL_CACHE[message_time].get('stored'):
                            slack_client.api_call(
                                "chat.postMessage",
                                channel="CBVS7HV1C",
                                text="What a popular comment! :star-struck:",
                                attachments=[SUGGESTED_MILESTONE]
                            )
                            print(message_time)
                            messages = slack_client_oauth.api_call(
                                "channels.history",
                                channel="CBVS7HV1C",
                                latest=message_time,
                                inclusive=True,
                                count=1
                            )
                            INTERNAL_CACHE[message_time]['text'] = messages['messages'][0]['text']
                            print("lenghth:   ", len(messages['messages']))
                            print(messages)
                            mongo.db.channel_history.insert(INTERNAL_CACHE[message_time])
                            INTERNAL_CACHE[message_time]['stored'] = True
                            print("wrote to database")
                    else:
                        INTERNAL_CACHE[message_time] = {}
                        INTERNAL_CACHE[message_time]['count'] = 1
                        INTERNAL_CACHE[message_time]['item'] = data['event']['item']
                if event_type == "app_mention" and "add" in event_text:
                    slack_client.api_call(
                        "chat.postMessage",
                        channel="CBVS7HV1C",
                        text="Good afternoon, let's add a milestone!",
                        attachments=[MANUAL_MILESTONE]
                    )
                if event_type == "app_mention" and "popular" in event_text:
                    [print(x['text']) for x in mongo.db.channel_history.find()]
                    text = ":triangular_flag_on_post: Here's a few memorable comments that have been said recently: \n"
                    for index, x in enumerate(list(mongo.db.channel_history.find({}, limit=4).sort([("timestamp", -1), ("id_", -1)]))):
                        text += ("\n" + str(index+1) + ") *" + x['text'] + "*\n")
                    slack_client.api_call(
                        "chat.postMessage",
                        channel="CBVS7HV1C",
                        text=text
                    )
                    print(text)
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
    return "Memory Bot added your memory!"
    #  return """
    #  <h1>Hello heroku</h1>
    #  <p>It is currently {time}.</p>
    #  <img src="http://loremflickr.com/600/400">
    #      """.format(time=the_time)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
