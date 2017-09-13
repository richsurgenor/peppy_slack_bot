import re
import os
import time
import subprocess
import urllib.request
from slackclient import SlackClient

#token = os.environ['TOKEN']
token = "xoxb-145318380262-GDqgBNxoaR0FazurLZi4lW4e"
dlurl = "https://files.slack.com/files-pri/T09ECU2SY-"

class PythonSlackBot(object):
    def __init__(self, slack_client, update_interval=1/4):
        self.slack_server = SlackServer(slack_client)

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
        self.slack_client.api_call("chat.postMessage", channel=channel, text=text, as_user='false', username='dat_bot',
        icon_url='https://avatars.slack-edge.com/2017-02-21/145321707046_478dcd6d7d66740c0082_72.jpg')

    def get_data(self):
        return self.slack_client.rtm_read()


def get_client():
    return SlackClient(token)


def run():
    print ("Starting Bot...")
    sc = get_client()
    if sc.rtm_connect():
        slack_server = SlackServer(sc)
        with PythonSlackBot(sc) as bot:
            while True:
                #print(slack_server.get_list_of_channels())
                #print(slack_server.get_list_of_private_ch())
                #slack_server.post_message("G72J6HJRJ", "test")
                data = slack_server.get_data()
                #todo detect if snippet is truncated and if so download url
                if len(data) > 0:
                    #print (data)
                    for item in data:
                            #todo implement type logging

                        if 'bot_id' in item == 'None':
                            pass

                        elif 'file' in item and 'text' in item:
                            channel = item['channel']
                            #user = item['user'] # could be used to manage py sessions...? group sessions could be a thing



                            #if 'preview_is_truncated' in item['file'] and item['file']['preview_is_truncated'] is True:
                            #    slack_server.post_message(channel, "Truncated snippets are not yet supported.")

                            #py_file_link = str(item['file']['id'])
                            #py_file_link = dlurl + py_file_link + "/download/-.py"
                            #py_file = download(py_file_link)
                            py_file_link = item['file']['url_private_download']
                            slack_server.post_message(channel, py_file_link)
                            text = download(py_file_link)
                            slack_server.post_message(channel, text)
                            #slack_server.post_message(channel, item['file']['url_private'])

                            #if item['type' == 'message':
                print(data)

                time.sleep(1/2)

    else:
        print ("Could not connect, please check API token.")


def download(url):
    #todo move the dl of file somewhere else
    request = urllib.request.Request(url)
    request.add_header("Authorization", "Bearer xoxb-145318380262-GDqgBNxoaR0FazurLZi4lW4e")
    result = urllib.request.urlopen(request)
    data = result.read()
    text = data.decode('utf-8')

    return text

class ChannelDoesNotExist(Exception):
    pass


if __name__ == "__main__":
    run()
