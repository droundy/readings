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
def index(name=None):
    today=schedule[1][daynum]
    link = 'https://www.biblestudytools.com/passage/?q='
    link += ';'.join([r.linkname for r in today])
    passage = ';'.join([r.name for r in today])

    return flask.render_template('index.html', link=link, today=today, passage=passage)

if __name__ == "__main__":
    app.run()
