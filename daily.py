import ClassRoom
import pickle
from datetime import date
from bot import line_bot_api
from reply import here
import os

from linebot.models import TextSendMessage

def send_daily(userid):
    classroom = pickle.load(open("datas/"+userid+".pickle", "rb")) # type: ClassRoom.ClassRoom
    resultstr = classroom.today(date.today())
    line_bot_api.push_message(userid, TextSendMessage(text=resultstr))

def main():
    for path in os.listdir(os.path.join(here(), "datas")):
        if not path.endswith(".pickle"):
            continue
        send_daily(path[:-7])

main()
