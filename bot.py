import os
import sys
import time
import urllib.request
import requests
import subprocess
import multiprocessing.connection
import socket
import fcntl
from slackclient import SlackClient


#token = os.environ['TOKEN']
TOKEN = "xoxb-243034904402-tYYxwikeot6EkM5t5455mDO1"
BOT_NAME = 'buggs'


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
        self.slack_client.api_call("chat.postMessage", channel=channel, text=text, as_user='false', username=BOT_NAME,
        icon_url='https://avatars.slack-edge.com/2017-09-19/243786869602_923e5e31f161f4a58fa9_48.png')
        #icon_url='https://avatars.slack-edge.com/2017-02-21/145321707046_478dcd6d7d66740c0082_72.jpg')

    def get_data(self):
        return self.slack_client.rtm_read()


def get_client():
    return SlackClient(TOKEN)

def process_interpreter(interpreter_handler, slack_server):
        for owner in interpreter_handler.interpreters.keys():
            interpreter = interpreter_handler.interpreters[owner]
            line = interpreter_handler.read_line(owner)
            chl = interpreter[0]

            if not line:
                line = interpreter_handler.read_err(owner)

            if line:
                slack_server.post_message(chl, line)


def run():
    print ("Starting Bot...")
    sc = get_client()
    time.sleep(1/4)
    interpreter_handler = PyInterpreters()
    if sc.rtm_connect():
        slack_server = SlackServer(sc)
        upload("blah", "G72J6HJRJ")
        with PythonSlackBot(sc) as bot:
            while True:
                process_interpreter(interpreter_handler, slack_server)
                data = slack_server.get_data()
                #todo detect if snippet is truncated and if so download url
                if len(data) > 0:
                    #print (data)
                    for item in data:
                            #todo implement type logging
                        if 'channel' in item and 'user' in item:
                            channel = item['channel']
                            user = item['user'] # could be used to manage py sessions...? group sessions could be a thing
                            if 'text' in item and item['text'] == "<@U7510SLBU> kill":
                                interpreter_handler.shutdown_interpreter(user + str(channel))
                                slack_server.post_message(channel, "The interpreter instance has been killed")
                            elif 'text' in item and item['text'] == "<@U7510SLBU> killall":
                                interpreter_handler.shutdown_interpreters()
                                slack_server.post_message(channel, "rip interpreters")

                            elif 'bot_id' in item == 'None':
                                pass

                            elif 'file' in item and 'text' in item and item['file']['filetype'] == 'python':



                                #if 'preview_is_truncated' in item['file'] and item['file']['preview_is_truncated'] is True:
                                #    slack_server.post_message(channel, "Truncated snippets are not yet supported.")

                                #py_file_link = str(item['file']['id'])
                                #py_file_link = dlurl + py_file_link + "/download/-.py"
                                #py_file = download(py_file_link)
                                py_file_link = item['file']['url_private_download']
                                text = download(py_file_link)
                                if text == None:
                                    continue
                                lines = []
                                if "\n" in text:
                                    for line in text.split('\r\n'):
                                        lines.append(line + '\r\n')
                                else:
                                    print('THIS WAS ENTERED')
                                    lines.append(text)

                                lines.append('')

                                for index, line in enumerate(lines):
                                    if line == None:
                                        lines[index] = 'NEWLINE'

                                if not interpreter_handler.spawn_interpreter(user, channel, lines):
                                    #interpreter_handler.interpreters[user][0] = channel
                                    interpreter_handler.send_lines(user + str(channel), lines)

                                slack_server.post_message(channel, "Processed.")

            else:
                print ("Could not connect, please check API token.")


def download(url):
    #todo move the dl of file somewhere else
    request = urllib.request.Request(url)
    request.add_header("Authorization", "Bearer " + TOKEN)
    result = urllib.request.urlopen(request)
    data = result.read()
    text = None
    try:
        text = data.decode('utf-8')
    except:
        pass

    return text


def upload(contents, channel):
    options = {
        "token": TOKEN,
        "file": contents,
        "filename": "response.py",
        "title": "test",
        "channels": channel
    }


    r = requests.post("https://slack.com/api/files.upload", options)

    print(r.text)


class PyInterpreters(object):

    def __init__(self):
        self.user = None
        self.interpreters = {}
        self.cur_port = 10000

    def spawn_interpreter(self, owner, channel, lines):
        if owner + str(channel) in self.interpreters:
            return False
        port = self.cur_port
        while True:
            try:
                l = multiprocessing.connection.Listener(('localhost', int(self.cur_port)), authkey=b"secret")
                break
            except socket.error as ex:
                if ex.errno != 98:
                    raise
            self.cur_port += 1

        proc = subprocess.Popen((sys.executable, "interpreter.py", str(port)), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, universal_newlines = True )

        fcntl.fcntl(proc.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        fcntl.fcntl(proc.stderr.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

        conn = l.accept()

        for line in lines:
            conn.send(line)

        self.interpreters[owner + str(channel)] = [channel, conn, proc]
        return True


    def send_lines(self, owner_id, lines):
        conn = self.interpreters[owner_id][1]
        for line in lines:
            conn.send(line)

    def get_connection_by_owner(self, owner):
        if owner in self.interpreters:
            return self.interpreters[owner][1]

    def shutdown_interpreter(self, owner):
        if owner in self.interpreters:
            self.interpreters[owner][1].close()
            del self.interpreters[owner]

    def shutdown_interpreters(self):
        for key in self.interpreters.keys():
            self.interpreters[key][1].close()

        self.interpreters = {}

    def read_line(self, owner):
        try:
            if self.interpreters[owner][2].stdout.readable():
                line = self.interpreters[owner][2].stdout.readline()
                line = str(line)
                #print ('LINE READ : ' + line)
        except IOError:
            line = None

        return line


    def read_err(self, owner):
        try:
            if self.interpreters[owner][2].stderr.readable():
                line = self.interpreters[owner][2].stderr.readline()
        except IOError:
            line = None

        return line





class ChannelDoesNotExist(Exception):
    pass


if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        print ("CAUGHT EXCEPTION: " + e)
