import pickle, argparse, lectionary, scriptures, random

parser = argparse.ArgumentParser(description='Schedule the lectionary readings.')
parser.add_argument('days', action='store', type=int)

args = parser.parse_args()
print(args)

print(args.days)
for i in range(args.days):
    lectionary.schedule_day()

for d in range(len(lectionary.schedule[1])):
    print('day', d)
    for r in lectionary.schedule[1][d]:
        print('   ',r)

lectionary.save_schedule()
