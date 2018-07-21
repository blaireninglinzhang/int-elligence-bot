import os
import json
import time
import re
from slackclient import SlackClient
from slackeventsapi import SlackEventAdapter


# slack_client = SlackClient('xoxb-369235392373-402130295793-JB7yKDAzWZ9DnKtehmWGxlYA')
BOT_TOKEN = "xoxb-369235392373-402130295793-JB7yKDAzWZ9DnKtehmWGxlYA"
CHANNEL_NAME = "int-elligence"

slack_events_adapter = SlackEventAdapter("NExx1buddCGoKEtFOwYJ2Gkb", endpoint="/slack/events")

# Create an event listener for "reaction_added" events and print the emoji name
@slack_events_adapter.on("reaction_added")
def reaction_added(event_data):
  event = event_data["event"]
  emoji = event["reaction"]
  print(event)
  print(emoji)

slack_events_adapter.start(port=8000)

def main():
    # Create the slackclient instance
    sc = SlackClient(BOT_TOKEN)

    # Connect to slack
    if sc.rtm_connect():
        # Send first message
        sc.rtm_send_message(CHANNEL_NAME, "I'm ALIVE!!!")

        while True:
            # Read latest messages
            # TODO: use emoji to do something
            
            for slack_message in sc.rtm_read():
                message = slack_message.get("text")
                user = slack_message.get("user")
                if not message or not user:
                    continue
                sc.rtm_send_message(CHANNEL_NAME, "<@{}> wrote something...".format(user))
            # Sleep for half a second
            time.sleep(0.5)
    else:
        print("Couldn't connect to slack")

if __name__ == '__main__':
    main()
