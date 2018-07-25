import pickle, lectionary, flask

app = flask.Flask(__name__)

with open("readings", "rb") as f:
    blocks = pickle.load(f)
with open("schedule", "rb") as f:
    schedule = pickle.load(f)

@app.route("/")
def index(name=None):
    today=schedule[-1]
    link = 'https://www.biblestudytools.com/passage/?q='
    link += ';'.join([r.linkname for r in today])
    passage = ';'.join([r.name for r in today])

    return flask.render_template('index.html', link=link, today=today, passage=passage)

if __name__ == "__main__":
    app.run()
