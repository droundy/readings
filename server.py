import pickle, lectionary, flask, datetime, glob, sys

app = flask.Flask(__name__)

@app.route("/")
def index():
    now = datetime.date.today()
    with open("schedule", "rb") as f:
        schedule = pickle.load(f)
    daynum = int((now - schedule[0]).total_seconds()/24/60/60)
    print(daynum)
    return day(daynum)

@app.route("/day-<int:daynum>")
def day(daynum):
    with open("readings", "rb") as f:
        blocks = pickle.load(f)
    with open("schedule", "rb") as f:
        schedule = pickle.load(f)
    modified_schedule = False
    while len(schedule[1]) <= daynum and daynum < 10000:
        lectionary.schedule_day(blocks, schedule)
        modified_schedule = True
    if modified_schedule:
        with open("schedule", "wb") as f:
            pickle.dump(schedule, f)
        with open("readings", "wb") as f:
            pickle.dump(blocks, f)
    today=lectionary.coalesce_readings(schedule[1][daynum])
    tomorrow = daynum+1
    yesterday = daynum-1
    if yesterday < 0:
        yesterday = None
    date = (schedule[0] + datetime.timedelta(daynum)).strftime("%A %B %e, %Y")
    niv_link = 'https://www.biblestudytools.com/passage/?q='
    niv_link += ';'.join([r.linkname for r in today])
    # The following is the oremus bible version: no adds!
    link = 'http://bible.oremus.org/?version=NRSV&vnum=NO&passages='
    link += '%0D%0A'.join([r.linkname for r in today])
    passage = '<br/>'.join(sorted([r.name for r in today]))

    return flask.render_template('index.html',
                                 date=date,
                                 link=link,
                                 niv_link=niv_link,
                                 today=today,
                                 passage=passage,
                                 yesterday=yesterday, tomorrow=tomorrow)

@app.route("/edit", methods=['GET'])
def edit():
    return flask.render_template('edit.html')

@app.route("/edit", methods=['POST'])
def submit_edit():
    form = flask.request.form
    feedback=None
    changes=None
    if 'passage' in form and len(form['passage']) > 0:
        try:
            feedback, passages_changed = lectionary.modify_readings(form['passage'],
                                                                    form['topics'].split(),
                                                                    'kids' in form)
            changes = 'Modified ' + ', '.join(sorted([r.name for r in passages_changed]))
            feedback = feedback.replace('\n', '<br/>')
        except:
            feedback = 'error modifying readings: {}'.format(sys.exc_info())
            changes = 'Error modifying readings'

    return flask.render_template('edit.html',
                                 changes=changes,
                                 feedback=feedback)

if __name__ == "__main__":
    app.run(extra_files=glob.glob('templates/*.html'))
