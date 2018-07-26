import pickle, datetime

today = datetime.date.today()
with open("schedule", "wb") as f:
    pickle.dump((today, []), f)
