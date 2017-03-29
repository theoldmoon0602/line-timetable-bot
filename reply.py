import ClassRoom
import pickle
from os import mkdir
from os.path import join, abspath, exists, dirname
from datetime import date

def here():
    return dirname(abspath(__file__))

def reply(msg, userid):
    datadir = join(here(), 'datas')
    datapath = join(datadir, userid + ".pickle")
    if not exists(datadir):
        mkdir(datadir)

    classroom = None
    if exists(datapath):
        classroom = pickle.load(open(datapath, "rb"))
    else:
        classroom = ClassRoom.ClassRoom()

    if msg.startswith('/class'):
        result_class = ClassRoom.parse_class(msg)
        if not result_class:
            return False
        classroom.add_class(result_class)
        pickle.dump(classroom, open(datapath, "wb"))
        return "OK"
    elif msg.startswith('/day'):
        day, class_definitions = ClassRoom.parse_day(msg)
        if not day:
            return False
        for c in class_definitions:
            classroom.add_class(c)
        classroom.add_day(day)
        pickle.dump(classroom, open(datapath, "wb"))
        return "OK"
    elif msg.startswith('/hwlist'):
        homework_list = ClassRoom.parse_list_homework(msg)
        if not homework_list:
            return False
        result = classroom.list_homeworks(homework_list, expire_date=date.today())
        return result
    elif msg.startswith('/hw'):
        homework = ClassRoom.parse_homework(msg)
        if not homework:
            return False
        classroom.add_homework(homework)
        pickle.dump(classroom, open(datapath, "wb"))
        return "OK"
    elif msg.startswith('/change'):
        change, class_definitions = ClassRoom.parse_change(msg)
        if not change:
            return False
        for c in class_definitions:
            classroom.add_class(c)
        classroom.change(change)
        pickle.dump(classroom, open(datapath, "wb"))
        return "OK"
    elif msg.startswith('/today'):
        resultstr = classroom.today(date.today())
        return resultstr
    return False
