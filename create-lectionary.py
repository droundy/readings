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

def book_block(b):
    readings = []
    cl = b.chapter_lengths
    for c in range(b.num_chapters):
        readings.append(Reading(b.name, '{}:1-{}:{}'.format(c+1, c+1, cl[c]),
                                   len(bible.get(books=[b.name], chapters=[c+1]))))
    return Block(b.name, readings)

blocks = set()

NT_total = 0
for x in nt[4:]:
    b = book_block(x)
    b.category = 'NT'
    blocks.add(b)
    print(b, len(b.readings), b.length)
    NT_total += b.length

gospels_total = 0
for x in nt[:4]:
    b = book_block(x)
    b.category = 'gospel'
    blocks.add(b)
    print(b, len(b.readings), b.length)
    gospels_total += b.length

OT_total = 0
Psalms_total = 0
for x in ot:
    b = book_block(x)
    b.category = 'OT'
    if b.name == 'Psalms':
        print('\n', b, b.length)
        for y in b.readings:
            n = str(y)
            bb = Block(n[:n.find(':')].replace('Psalms', 'Psalm'), [y])
            bb.category = 'Psalms'
            blocks.add(bb)
            print(bb, len(bb.readings), bb.length)
            Psalms_total += y.length
    else:
        blocks.add(b)
        print(b, len(b.readings), b.length)
        OT_total += b.length

print('gospels:', gospels_total)
print('NT:', NT_total)
print('OT:', OT_total)
print('Psalms:', Psalms_total)

print(blocks)

with open("readings", "wb") as f:
    pickle.dump(blocks, f)
