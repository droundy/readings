import pickle, lectionary, flask, datetime

app = flask.Flask(__name__)

with open("readings", "rb") as f:
    blocks = pickle.load(f)
with open("schedule", "rb") as f:
    schedule = pickle.load(f)

now = datetime.date.today()
daynum = int((now - schedule[0]).total_seconds()/24/60/60)
print(daynum)

@app.route("/")
def index():
    return day(daynum)

@app.route("/day-<int:daynum>")
def day(daynum):
    while len(schedule[1]) <= daynum and daynum < 10000:
        lectionary.schedule_day(blocks, schedule)
    today=lectionary.coalesce_readings(schedule[1][daynum])
    tomorrow = daynum+1
    yesterday = daynum-1
    if yesterday < 0:
        yesterday = None
    niv_link = 'https://www.biblestudytools.com/passage/?q='
    niv_link += ';'.join([r.linkname for r in today])
    # The following is the oremus bible version: no adds!
    link = 'http://bible.oremus.org/?version=NRSV&vnum=NO&passages='
    link += '%0D%0A'.join([r.linkname for r in today])
    passage = '; '.join([r.name for r in today])

    return flask.render_template('index.html',
                                 link=link,
                                 niv_link=niv_link,
                                 today=today,
                                 passage=passage,
                                 yesterday=yesterday, tomorrow=tomorrow)

if __name__ == "__main__":
    app.run()
