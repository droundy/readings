import pickle, argparse, lectionary, scriptures

parser = argparse.ArgumentParser(description='Modify the lectionary readings.')
parser.add_argument('passage', action='store', nargs='+')
args = parser.parse_args()

with open("readings", "rb") as f:
    blocks = pickle.load(f)

passages = scriptures.extract(' '.join(args.passage))

for (book, chapter1, verse1, chapterN, verseN) in passages:
    r = lectionary.Reading(book, chapter1, verse1,
                           chapterN, verseN)
    print(r)
    for b in blocks:
        if b.name == 'Psalm 23':
            print(b)
            for r in b.readings:
                print('   ', r)

