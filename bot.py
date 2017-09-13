import re
import os
import time
from slackclient import SlackClient

token = "xoxb-145318380262-9rA9lk1J2JM2mLvBIQGgSIR7"


class PythonSlackBot(object):
    def __init__(self, slack_client, update_interval=1/4):
        self.slack_server = SlackServer(slack_client)
        self.token = 3

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        pass

class SlackServer(object):
    def __init__(self, slack_client):
        self.slack_client = slack_client

    def get_list_of_channels(self):
        return self.slack_client.api_call("channels.list")["channels"]

    def get_list_of_private_ch(self):
        return self.slack_client.api_call("groups.list")

    def get_channel_name_by_id(self, channel_id):
        for channel in self.get_list_of_channels():
            if channel['id'] == channel_id:
                return channel['name']
        raise ChannelDoesNotExist(channel_id)

    def get_channel_id_by_name(self, channel_name):
        for channel in self.get_list_of_channels():
            if channel['name'] == channel_name:
                return channel['id']
        raise ChannelDoesNotExist(channel_name)

    def post_message(self, channel, text):
        self.slack_client.api_call("chat.postMessage", channel=channel, text=text)

    def get_data(self):
        return self.slack_client.rtm_read()


def get_client():
    return SlackClient(token)


def run():
    sc = get_client()
    if sc.rtm_connect():
        slack_server = SlackServer(sc)
        with PythonSlackBot(sc) as bot:
            while True:
                #print(slack_server.get_list_of_channels())
                print(slack_server.get_list_of_private_ch())
                slack_server.post_message("G72J6HJRJ", "test")
                data = slack_server.get_data()
                if len(data) > 0:
                    print (data)

                time.sleep(10)


class ChannelDoesNotExist(Exception):
    pass


if __name__ == "__main__":
    run()
