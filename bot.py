from flask import Flask
from linebot import LineBotApi, WebhookHandler
import os

import logging

from os.path import join, dirname, abspath

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

debug_handler = logging.FileHandler(join(dirname(abspath(__file__)), 'log.txt'), delay=True)
debug_handler.setLevel(logging.DEBUG)

errorlog_handler = logging.FileHandler(join(dirname(abspath(__file__)), "error.txt"), delay=True)
errorlog_handler.setLevel(logging.ERROR)

app.logger.addHandler(debug_handler)
app.logger.addHandler(errorlog_handler)
app.logger.setLevel(logging.DEBUG)


