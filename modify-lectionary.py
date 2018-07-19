from pysword.bible import SwordBible
import pickle

bible = SwordBible('/usr/share/sword/modules/texts/ztext/kjv/',
                   'ztext', 'kjv', 'utf8', 'OSIS')

structure = bible.get_structure()

books = structure.get_books()

nt = books['nt']

ot = books['ot']

class Reading:
    """A reading that may be scheduled in a single day"""
    def __init__(self, book, verses, length):
        self.book = book
        self.verses = verses
        self.length = length
    def __str__(self):
        return '{} {}'.format(self.book, self.verses)
    def __repr__(self):
        return '{} {}'.format(self.book, self.verses)

class Block:
    """A block of readings that should be scheduled consecutively"""
    def __init__(self, name, readings):
        self.name = name
        self.readings = readings
        self.category = ''
        self.length = sum([r.length for r in readings])
    def __str__(self):
        return '{}'.format(self.name)
    def __repr__(self):
        return '{}'.format(self.name)

with open("readings", "rb") as f:
    blocks = pickle.load(f)

for b in blocks:
    print(b)
    for r in b.readings:
        print('   ', r)
