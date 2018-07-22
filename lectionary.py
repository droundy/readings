from pysword.bible import SwordBible
import pickle, scriptures

bible = SwordBible('/usr/share/sword/modules/texts/ztext/kjv/',
                   'ztext', 'kjv', 'utf8', 'OSIS')

structure = bible.get_structure()

books = structure.get_books()

class Reading:
    """A reading that may be scheduled in a single day"""
    def __init__(self, book, chap1, verse1, chapN, verseN, topics=set(), kids=False):
        self.length = passage_length(book, chap1, verse1, chapN, verseN)
        if book == 'Revelation of John':
            book = 'Revelation'
        self.book = book
        self.chap1 = chap1
        self.verse1 = verse1
        self.chapN = chapN
        self.verseN = verseN
        self.topics = topics
        self.kids = kids
    def __str__(self):
        return '{} ({})'.format(self.name, self.length)
    def __repr__(self):
        return self.name
    @property
    def name(self):
        tags = ''
        if len(self.topics) > 0:
            tags = ' ({})'.format(', '.join(self.topics))
        prefix = ''
        if self.kids:
            prefix = '*'
        n = prefix + scriptures.reference_to_string(self.book,
                                                    self.chap1, self.verse1,
                                                    self.chapN, self.verseN) + tags
        n = n.replace(' of Jesus Christ','')
        return n
    def __eq__(self, r):
        return (self.book == r.book
                and self.chap1 == r.chap1 and self.chapN == r.chapN
                and self.verse1 == r.verse1 and self.verseN == r.verseN)
    def __lt__(self, r):
        return (self.chapN < r.chap1
                or (self.chapN == r.chap1 and self.verseN < r.verse1))
    def __le__(self, r):
        return not self > r
    def __gt__(self, r):
        return (self.chap1 > r.chapN
                or (self.chap1 == r.chapN and self.verse1 > r.verseN))
    def __ge__(self, r):
        return not self < r
    def overlaps(self, r):
        return self.book == r.book and (self == r or (self >= r and self <= r))
    def __sub__(self, r):
        if not self.overlaps(r):
            return [self]
        if r == self:
            return []
        chunks = []
        if self <= r:
            if r.verse1==1:
                b,c1,v1,cN,vN = scriptures.normalize_reference(self.book,
                                                               self.chap1, self.verse1,
                                                               r.chap1-1)
            else:
                b,c1,v1,cN,vN = scriptures.normalize_reference(self.book,
                                                               self.chap1, self.verse1,
                                                               r.chap1, r.verse1-1)
            chunks.append(Reading(b, c1, v1, cN, vN))
        if self >= r:
            try:
                b,c1,v1,cN,vN = scriptures.normalize_reference(self.book,
                                                               r.chapN, r.verseN+1,
                                                               self.chapN, self.verseN)
            except:
                b,c1,v1,cN,vN = scriptures.normalize_reference(self.book,
                                                               r.chapN+1,
                                                               end_chapter=self.chapN,
                                                               end_verse=self.verseN)
            chunks.append(Reading(b, c1, v1, cN, vN))
        return chunks

class Block:
    """A block of readings that should be scheduled consecutively"""
    def __init__(self, name, readings):
        if name == 'Revelation of John':
            name = 'Revelation'
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
