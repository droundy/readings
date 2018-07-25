import pickle, argparse, lectionary, scriptures, random

parser = argparse.ArgumentParser(description='Schedule the lectionary readings.')
parser.add_argument('days', action='store', nargs=1, type=int)

args = parser.parse_args()
print(args)

with open("readings", "rb") as f:
    blocks = pickle.load(f)
with open("schedule", "rb") as f:
    schedule = pickle.load(f)

current_blocks = [b for b in blocks if b.where_am_i is not None]

categories = ['gospel', 'NT', 'OT', 'Psalms']
years = [0.8,1,2,1.5]
goals = []
have_read = []
priority = []

num_days = len(schedule[1])

for i in range(len(categories)):
    total = sum([b.length for b in blocks if b.category == categories[i]])
    goals.append(total/365.0/years[i])
    print(categories[i], 'daily goal', goals[i])
    have_read.append(sum([r.length for day in schedule[1] for r in day if r.category == categories[i]]))
    print('    in', num_days, 'days have read', have_read[i])
    priority.append((num_days+1)*goals[i] - have_read[i])
    print('    priority', priority[i])

print('currently reading', current_blocks)

today = []
for x in range(2*len(categories)):
    most_needed = max(priority)
    if most_needed < 0:
        break
    for i in range(len(categories)):
        c = categories[i]
        if priority[i] == most_needed:
            print('need', c, 'most')
            now = [b for b in current_blocks if b.category == c]
            if len(now) == 0:
                print('picking new', c, 'block')
                least_read = min([b.times_read for b in blocks if b.category == c])
                options = [b for b in blocks if b.category == c and b.times_read == least_read]
                b = random.choice(options)
                b.where_am_i = 0
            else:
                b = now[0]
            length = 0
            while length < most_needed:
                r = b.readings[b.where_am_i]
                print('adding', r)
                b.where_am_i += 1
                length += r.length
                priority[i] -= r.length
                today.append(r)
                if b.where_am_i >= len(b.readings): # we have finished this block
                    b.where_am_i = None
                    try:
                        current_blocks.remove(b)
                    except:
                        pass
                    break

schedule[1].append(today)

for d in range(len(schedule[1])):
    print('day', d)
    for r in schedule[1][d]:
        print('   ',r)

with open("readings", "wb") as f:
    pickle.dump(blocks, f)
with open("schedule", "wb") as f:
    pickle.dump(schedule, f)
