import pickle, argparse, lectionary, scriptures

parser = argparse.ArgumentParser(description='Modify the lectionary readings.')
parser.add_argument('passage', action='store', nargs='+')
parser.add_argument('--kids', action='store_true')
parser.add_argument('--no-kids', action='store_true')
parser.add_argument('--tag', action='append', default=[])

args = parser.parse_args()
print(args)

with open("readings", "rb") as f:
    blocks = pickle.load(f)

passages = scriptures.extract(' '.join(args.passage))
print('passages are', passages,'from', ' '.join(args.passage))

for (book, chapter1, verse1, chapterN, verseN) in passages:
    r = lectionary.Reading(book, chapter1, verse1,
                           chapterN, verseN)
    if args.kids:
        r.kids = True
    if args.no_kids:
        r.kids = False
    for t in args.tag:
        r.topics.add(t)
    print(r)
    for b in blocks:
        new_readings = set()
        old_readings = set()
        for rr in b.readings:
            if rr.book != r.book:
                break
            if rr.overlaps(r):
                print(r, 'overlaps', rr)
                print(rr - r)
                old_readings.add(rr)
                for rrr in rr-r:
                    new_readings.add(rrr)
                new_readings.add(r)
        if len(new_readings) > 0:
            for rr in old_readings:
                b.readings.remove(rr)
            b.readings.extend(new_readings)
            b.readings.sort()
            for rr in b.readings:
                print('   ', rr)

with open("readings", "wb") as f:
    pickle.dump(blocks, f)

