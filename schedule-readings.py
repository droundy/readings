import pickle, argparse, lectionary, scriptures, random

parser = argparse.ArgumentParser(description='Schedule the lectionary readings.')
parser.add_argument('days', action='store', type=int)

args = parser.parse_args()
print(args)

with open("readings", "rb") as f:
    blocks = pickle.load(f)
with open("schedule", "rb") as f:
    schedule = pickle.load(f)

print(args.days)
for i in range(args.days):
    lectionary.schedule_day(blocks, schedule)

for d in range(len(schedule[1])):
    print('day', d)
    for r in schedule[1][d]:
        print('   ',r)

with open("readings", "wb") as f:
    pickle.dump(blocks, f)
with open("schedule", "wb") as f:
    pickle.dump(schedule, f)
