import os
import json
import time
import re
from slackclient import SlackClient


# instantiate Slack client
slack_client = SlackClient('xoxp-369235392373-394289804691-402685810066-a1f17bba5172e3d876455962b7796c6e')
bot_client = SlackClient('xoxb-369235392373-404015005318-fwClSJ0ywbTWjjckqbFTeE4P')
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None



# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
DO_COMMAND = "history"
HELLO_COMMAND = 'hello'
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"
channel_code = "CBVS7HV1C"


def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None


def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)


def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try {0}.".format(DO_COMMAND)

    # Finds and executes the given command, filling in response
    response = None

    # This is where you start to implement more commands!
    if command.startswith(DO_COMMAND):
        response = "Tracking History"

        
        history = slack_client.api_call(
                            "channels.history",
                              channel = channel_code,
                              )
        #print(history)

        history_list = history["messages"]

        timestamp = 0 #testing
        
        count = 0
        print(history_list[0])
        for i in history_list:
            reaction_index = 0
            reaction_count = 0
            
            if "reactions" in history_list[count]:
                for j in history_list[count]["reactions"]:
                    reaction_count += history_list[count]["reactions"][reaction_index]["count"]
                    reaction_index += 1
            #print(reaction_count)
            count += 1
            
        timestamp = history["messages"][0]["ts"]
      
        #print("timestamp: " + timestamp)

        
        reactions = slack_client.api_call(
            "reactions.get",
            channel = channel_code,
            name = "thumbsup",
            timestamp= timestamp
            )

        #print(reactions)              
    elif command.startswith(HELLO_COMMAND):
        response = "Hi everyone! I'm a bot, bleep, bloop."

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )


if __name__ == "__main__":
    if bot_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")

        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = bot_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(bot_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
