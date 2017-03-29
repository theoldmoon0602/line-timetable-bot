# LINE TIMETABLE BOT

## env

python3.5 or later

## usage
$ pip install -r requirements.txt
$ export CHANNEL\_ACCESS\_TOKEN='\<your access token\>'
$ export CHANNEL\_SECRET='\<your secret token\>'
$ python index.py

## files
- bot.py: a library for using line messaging api
- ClassRoom.py: a library for data structure
- index.py: a flask web server which get a callback from line
- daily.py: a script which emit /today message to each channels

- app.wsgi: wsgi script file for used by mod\_wsgi3
