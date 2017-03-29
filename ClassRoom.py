import re
import datetime
from collections import defaultdict
from itertools import chain

class Class:
    """授業を表す"""

    def __init__(self, name, teacher, additionals):
        self.name = name
        self.teacher = teacher
        self.additionals = additionals

    def __repr__(self):
        return '<Class {} by {} {}>'.format(self.name, self.teacher, self.additionals)

    def __str__(self):
        result = ["{} {}".format(self.name, self.teacher)]
        for k, v in self.additionals.items():
            result.append("\t{}:\t{}".format(k, v))
        return "\n".join(result)


class Day:
    """ある日をあらわす"""

    def __init__(self, weekday):
        if not 0 <= weekday <= 6:
            raise ValueError
        self.weekday = weekday
        self.times = {}

    def __repr__(self):
        return '<Day {} {}>'.format(self.weekday, self.times)

    def set_class(self, time, class_name):
        self.times[time] = class_name

class Homework:
    """課題を表す"""

    def __init__(self, date, class_name, text):
        self.date = date
        self.class_name = class_name
        self.text = text

    def __repr__(self):
        return '<Homework {} at {:%Y/%m/%d} "{}">'.format(self.class_name, self.date, self.text)

    def __str__(self):
        return '{} {}'.format(self.class_name, self.text)


class Change(Day):
    """授業変更"""

    def __init__(self, date):
        Day.__init__(self, date.weekday())
        self.date = date

    def __repr__(self):
        return '<Change {:%Y/%m/%d}>'.format(self.date)


class ClassRoom:
    """クラスを司る神"""

    def __init__(self):
        self.classes = {}
        self.days = {}
        self.homeworks = defaultdict(list)
        self.changes = defaultdict(list)

    def add_class(self, cls: Class):
        """授業を追加する"""
        self.classes[cls.name] = cls

    def add_day(self, day: Day):
        """ある曜日を追加する"""
        self.days[day.weekday] = day

    def add_homework(self, homework: Homework):
        """homeworkを追加する"""
        self.homeworks[homework.date].append(homework)

    def list_homeworks(self, filter_predicate, expire_date = datetime.date.today()):
        flatten_homeworks = chain.from_iterable(self.homeworks.values())
        valid_homeworks = filter(lambda x: x.date >= expire_date, flatten_homeworks)
        homeworks = filter(filter_predicate, valid_homeworks)
        homeworks = sorted(homeworks, key=lambda x: x.date)

        output = []
        for hw in homeworks:
            output.append("{:%Y/%m/%d} {} {}".format(hw.date, hw.class_name, hw.text))
        return "\n".join(output)

    def change(self, change):
        self.changes[change.date].append(change)

    def today(self, date):
        todays_homeworks = self.homeworks.get(date, [])
        todays_changes = self.changes.get(date, [])

        day = self.days.get(date.weekday(), None)  # type: Day
        if not day:
            return ""

        for change in todays_changes:
            for time, class_name in change.times.items():
                day.times[time] = class_name

        output = []
        times = sorted(day.times.items(), key=lambda x: x[0])
        times.append([False, False])
        prev_class = False
        ts = []
        for t, c in times:
            if prev_class is not False and c != prev_class:
                output.append("{}: {}".format(", ".join(ts), self.classes.get(prev_class, "unknown class " + prev_class)))
                output.extend(["\t課題:\t" + hw.text for hw in todays_homeworks if hw.class_name == prev_class])
                ts = []
            ts.append(str(t))
            prev_class = c
        return "\n".join(output)

class Parser:
    def __init__(self, s):
        self.s = s
        self.p = 0

        self.skip()

    def skip(self, pred=lambda x: x in [" ", "\n", "\r", "　"]):
        while not self.end() and pred(self.s[self.p]):
            self.p += 1

    def getn(self, l: int):
        return self.s[self.p:self.p + l]

    def read(self, s: str):
        if self.getn(len(s)) == s:
            self.p += len(s)
            self.skip()
            return s
        return None

    def match(self, pat):
        res = pat.match(self.s[self.p:])
        if not res:
            return None
        matched = res.group(0)
        return self.read(matched)

    def end(self):
        return self.p >= len(self.s)

    def remained(self):
        return self.s[self.p:]


def parse_class_definition(p: Parser):
    word = re.compile(r"\D\w*", re.UNICODE)
    additional_begin = re.compile(r"[(（]\w+", re.UNICODE)
    additional_end = re.compile(r"\w+[）)]", re.UNICODE)

    name = p.match(word)
    if not name:
        return None, None, None

    teacher = p.match(word)
    if not teacher:
        return name, None, {}

    additionals = {}
    while not p.end():
        k = p.match(additional_begin)
        if not k:
            break
        v = p.match(additional_end)
        if not v:
            break
        additionals[k[1:]] = v[:-1]
    return name, teacher, additionals


def parse_class(opstr):
    p = Parser(opstr)
    if not p.read("/class"):
        return None

    name, teacher, additionals = parse_class_definition(p)
    if not name or not teacher:
        return None
    return Class(name, teacher, additionals)


def weekday2i(weekday):
    try:
        return "月火水木金土日".index(weekday)
    except:
        return None


def parse_times(p):
    times_pattern = re.compile(r"\d+(\s*[,、]\s*\d+)*", re.UNICODE)
    times_split = re.compile(r"\s*[,、]\s*", re.UNICODE)

    times = p.match(times_pattern)
    if not times:
        return None
    times = [int(t) for t in times_split.split(times)]
    if not times:
        return None

    return times


def parse_day(opstr):
    p = Parser(opstr)
    if not p.read("/day"):
        return None, None

    day_pattern = re.compile(r"[(（]\w+[）)]", re.UNICODE)

    weekday = p.match(day_pattern)
    if not weekday:
        return None, None
    weekday = weekday2i(weekday[1:-1])
    if weekday is None:
        return None, None

    day = Day(weekday)
    class_definitions = []
    while not p.end():
        times = parse_times(p)
        if not times:
            return None, None

        name, teacher, optionals = parse_class_definition(p)
        if not name:
            return None, None
        if teacher:
            class_definitions.append(Class(name, teacher, optionals))

        for time in times:
            day.set_class(time, name)
    return day, class_definitions


def parse_day_or_date(p):
    date_pattern = re.compile(r'[(（]\d+[/／]\d+[）)]', re.UNICODE)
    date_split_pattern = re.compile(r'[/／]', re.UNICODE)
    day_pattern = re.compile(r'[(（]\w+[）)]', re.UNICODE)

    deadline_date = p.match(date_pattern)
    date = None
    if deadline_date:
        m, d = map(int, date_split_pattern.split(deadline_date[1:-1]))
        date = datetime.date(year=datetime.date.today().year, month=m, day=d)
        if date < datetime.date.today():
            date.year += 1
        return date
    else:
        deadline_day = p.match(day_pattern)
        if not deadline_day:
            return None
        day = weekday2i(deadline_day[1:-1])
        date = datetime.date.today()
        while date.weekday() != day:
            date += datetime.timedelta(days=1)
        return date
    return None


def parse_homework(opstr):
    p = Parser(opstr)
    if not p.read("/hw"):
        return None

    date = parse_day_or_date(p)
    word_pattern = re.compile(r'\w+', re.UNICODE)
    class_name = p.match(word_pattern)
    if not class_name:
        return None
    text = p.remained().strip()

    return Homework(date, class_name, text)


def parse_list_homework(opstr):
    p = Parser(opstr)
    if not p.read("/hwlist"):
        return None

    date = parse_day_or_date(p)
    word_pattern = re.compile(r"\w+", re.UNICODE)
    class_name = p.match(word_pattern)

    def predicate(homework):
        if class_name and homework.class_name != class_name:
            return False
        if date and homework.date != date:
            return False
        return True

    return predicate


def parse_change(opstr):
    p = Parser(opstr)
    if not p.read("/change"):
        return None, None

    date = parse_day_or_date(p)
    if not date:
        return None, None

    change = Change(date)
    class_definitions = []
    while not p.end():
        times = parse_times(p)
        if not times:
            break

        class_name, teacher, additionals = parse_class_definition(p)
        if not class_name:
            break
        if teacher:
            class_definitions.append(Class(class_name, teacher, additionals))
        for time in times:
            change.set_class(time, class_name)
    return change, class_definitions
