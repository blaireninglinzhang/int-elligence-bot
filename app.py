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

@app.route('/', methods=['GET', 'POST'])
def homepage():
    if request.method == 'POST':
        # Slack sent a button press
        if request.content_type == "application/x-www-form-urlencoded":
            data = request.form
            print(data)
            return "hello"
        # Slack just sent an event
        elif request.content_type == "application/json":
            data = request.get_json()
            print(data)
            response = dict()
            if data.get('event', ''):
                event_type = data['event'].get('type', '')
                event_text = data['event'].get('text', '')[12:]
                if event_type == "app_mention":
                    slack_client.api_call(
                        "chat.postMessage",
                        channel="CBVS7HV1C",
                        text="yo waddup"
                    )
                    print(event_type, event_text)
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
