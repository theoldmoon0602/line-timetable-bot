import re
import os
import json
import traceback
from flask import abort, request
from bot import app, line_bot_api, handler
import reply

from linebot.models import MessageEvent, TextMessage, TextSendMessage, SourceUser, SourceGroup, SourceRoom

@app.route("/test", methods=['GET'])
def test():
    return 'working'

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    if not body:
        abort(400)
    app.logger.debug(body)

    try:
        handler.handle(body, signature)
    except Exception as e:
        app.logger.error(traceback.format_exc())
        abort(400)


    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    recved = event.message.text
    if recved.strip()[0] == '/':
        user_id = None
        if isinstance(event.source, SourceUser):
            user_id = event.source.user_id
        elif isinstance(event.source, SourceGroup):
            user_id = event.source.group_id
        else:
            user_id = event.source.room_id
        r = reply.reply(recved, user_id)
        if r is False:
            line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="Invalid command"))
            return
        
        line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=r))


if __name__ == "__main__":
    app.run(host='0.0.0.0')
