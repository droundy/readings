from pysword.bible import SwordBible
import pickle, scriptures

bible = SwordBible('/usr/share/sword/modules/texts/ztext/kjv/',
                   'ztext', 'kjv', 'utf8', 'OSIS')

structure = bible.get_structure()

books = structure.get_books()

class Reading:
    """A reading that may be scheduled in a single day"""
    def __init__(self, book, chap1, verse1, chapN, verseN):
        self.book = book
        self.chap1 = chap1
        self.verse1 = verse1
        self.chapN = chapN
        self.verseN = verseN
        self.length = passage_length(book, chap1, verse1, chapN, verseN)
    def __str__(self):
        return '{} ({})'.format(self.name, self.length)
    def __repr__(self):
        return self.name
    @property
    def name(self):
        return '{} {}:{}-{}:{}'.format(self.book, self.chap1, self.verse1,
                                       self.chapN, self.verseN)

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
        readings.append(Reading(b.name, c+1, 1, c+1, cl[c]))
    return Block(b.name, readings)

def passage_length(book, chap1, verse1, chapN, verseN):
    totlen = -1
    c = chap1
    v = verse1
    while c <= chapN:
        while c < chapN or v <= verseN:
            try:
                totlen += 1+len(bible.get(books=[book], chapters=[c], verses=[v]))
            except:
                break
            v += 1
        v=1
        c += 1
    return totlen
