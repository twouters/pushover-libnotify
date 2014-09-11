#!/usr/bin/env python
#

from xdg.BaseDirectory import xdg_config_home, xdg_cache_home
from PIL import Image
import configparser
import notify2
import requests
import os
import sys
import stat
import getpass
import websocket
import threading
import hashlib


config_file = os.path.join(xdg_config_home,'pushover-libnotify.conf')
config = configparser.RawConfigParser(allow_no_value=True)
if not os.path.isfile(config_file):
    config['pushover'] = {
            'userkey': '',
            'usersecret': '',
            'deviceid': '',
            'icon_size': [32,32]
            }
    with open(config_file, 'w') as cf:
        os.chmod(config_file, 0o600)
        config.write(cf)

config.read(config_file)
c = config['pushover']

if (c['userkey'] == '' or c['usersecret'] == ''):
    user = input('Pushover email: ')
    password = getpass.getpass('Pushover password (will not be saved): ')
    r = requests.post(
            'https://api.pushover.net/1/users/login.json',
            params=({'email':user, 'password':password})
            )
    result = r.json()
    if not result['status'] == 1:
        print('Unable to login. %s' % r.text)
        sys.exit()
    config['pushover']['userkey'] = result['id']
    config['pushover']['usersecret'] = result['secret']
    with open(config_file, 'w') as cf:
        config.write(cf)
    config.read(config_file)
    c = config['pushover']

if (c['deviceid'] == ''):
    devicename = os.uname()[1] + '-pushover-libnotify'
    r = requests.post(
            'https://api.pushover.net/1/devices.json',
            params=({'secret': c['usersecret'], 'name': devicename, 'os': 'O'})
            )
    result = r.json()
    if not result['status'] == 1:
        print('Could not register device: %s' % result['errors'])
        sys.exit()
    config['pushover']['deviceid'] = result['id']
    with open(config_file, 'w') as cf:
        config.write(cf)
    config.read(config_file)
    c = config['pushover']

def geticon(url):
    icon_size = [int(n) for n in c['icon_size'].split(',')]
    cache_dir = os.path.join(xdg_cache_home, 'pushover-libnotify', 'icons')
    if not os.path.isdir(cache_dir):
        os.makedirs(cache_dir)
    filename = os.path.join(cache_dir, hashlib.sha1(url.encode('utf8')).hexdigest())
    if not os.path.isfile(filename):
        with open(filename+'-full', 'wb') as f:
            response = requests.get(url, stream=True)
            for block in response.iter_content(1024):
                f.write(block)
        im = Image.open(filename+'-full')
        im.thumbnail(icon_size, Image.ANTIALIAS)
        im.save(filename, 'PNG')
        os.remove(filename+'-full')
    return 'file://' + filename

def fetch():
    r = requests.get(
            'https://api.pushover.net/1/messages.json',
            params=({'secret': c['usersecret'], 'device_id': c['deviceid']})
            )
    highest = 0
    for message in r.json()['messages']:
        notify(message)
        if message['id'] > highest:
            highest = message['id']
    r = requests.post(
            'https://api.pushover.net/1/devices/%s/update_highest_message.json' % (c['deviceid']),
            params=({'secret': c['usersecret'],'message': highest})
            )

def notify(data):
    notify2.init("Pushover-libnotify")
    title = data['app']
    if data['title'] != '':
        title += ' - '+data['title']
    if data['icon'] != 'default':
        icon = data['icon']
    else:
        icon = 'https://api.pushover.net/icons/pushover.png'
    icon = geticon(icon)
    n = notify2.Notification(
            title,
            data['message'],
            icon)
    n.show()

def on_message(ws, message):
    if message == b'!':
        # fetch last messages (threaded)
        fetch()
    if message == b'R':
        ws.close()

def on_error(ws, error):
    print(error)

def on_close(ws):
    print("### closed ###")

def on_open(ws):
    ws.send("login:%s:%s\n" % (c['deviceid'], c['usersecret']))

ws = websocket.WebSocketApp(
        "wss://client.pushover.net/push",
        on_message = on_message,
        on_error = on_error,
        on_close = on_close)

ws.on_open = on_open
ws.run_forever()

sys.exit()
