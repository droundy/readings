from pysword.bible import SwordBible
import pickle, scriptures, random, datetime, copy, inspect, os

bible = SwordBible(os.path.dirname(inspect.getfile(inspect.currentframe()))+'/kjv',
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
        self.topics = copy.copy(topics)
        self.kids = kids
        self.category = ''
    def __str__(self):
        return '{} ({})'.format(self.name, self.length)
    def __repr__(self):
        return self.name
    def __hash__(self):
        return hash(self.name)
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
    @property
    def linkname(self):
        n = scriptures.reference_to_string(self.book,
                                           self.chap1, self.verse1,
                                           self.chapN, self.verseN)
        n = n.replace(' of Jesus Christ','')
        return n
    @property
    def space_topics(self):
        return ' '.join(self.topics)
    @property
    def link(self):
        niv_link = 'https://www.biblegateway.com/passage/?search='
        niv_link += self.linkname+'&version=NIV'
        return niv_link
    def __eq__(self, r):
        return (self.book == r.book
                and self.chap1 == r.chap1 and self.chapN == r.chapN
                and self.verse1 == r.verse1 and self.verseN == r.verseN)
    def __lt__(self, r):
        return (self.book < r.book or
                (self.book == r.book
                 and (self.chapN < r.chap1 or (self.chapN == r.chap1 and self.verseN < r.verse1))))
    def __le__(self, r):
        return (self.book < r.book or
                (self.book == r.book
                 and (self.chap1 < r.chap1 or (self.chap1 == r.chap1 and self.verse1 <= r.verse1))))
    def __gt__(self, r):
        return (self.book > r.book or
                (self.book == r.book
                 and (self.chap1 > r.chapN or (self.chap1 == r.chapN and self.verse1 > r.verseN))))
    def __ge__(self, r):
        return (self.book > r.book or
                (self.book == r.book
                 and (self.chapN > r.chapN or (self.chapN == r.chapN and self.verseN >= r.verseN))))
    def overlaps(self, r):
        return self.book == r.book and (not self < r) and (not self > r)
    def __sub__(self, r):
        if not self.overlaps(r):
            return [self]
        if r == self:
            return []
        chunks = []
        if self <= r and (self.chap1 < r.chap1 or self.verse1 < r.verse1):
            if r.verse1==1:
                b,c1,v1,cN,vN = scriptures.normalize_reference(self.book,
                                                               self.chap1, self.verse1,
                                                               r.chap1-1)
            else:
                b,c1,v1,cN,vN = scriptures.normalize_reference(self.book,
                                                               self.chap1, self.verse1,
                                                               r.chap1, r.verse1-1)
            chunks.append(Reading(b, c1, v1, cN, vN))
        if self >= r and (self.chapN > r.chapN or self.verseN > r.verseN):
            print('hello', self, r)
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
    def __init__(self, name, readings, cat):
        if name == 'Revelation of John':
            name = 'Revelation'
        self.name = name
        self.readings = readings
        for r in readings:
            r.category = cat
        self.category = cat
        self.length = sum([r.length for r in readings])
        self.times_read = 0
        self.where_am_i = None
    def __str__(self):
        return '{}'.format(self.name)
    def __repr__(self):
        return '{}'.format(self.name)
    def __lt__(self, b):
        return self.name < b.name

def book_block(b, cat):
    readings = []
    cl = b.chapter_lengths
    for c in range(b.num_chapters):
        readings.append(Reading(b.name, c+1, 1, c+1, cl[c]))
    return Block(b.name, readings, cat)

with open("readings", "rb") as f:
    blocks = pickle.load(f)

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

def schedule_day(blocks, schedule):
    current_blocks = [b for b in blocks if b.where_am_i is not None]

    categories = ['NT', 'OT', 'Psalms']
    years = [1,2,1.5]
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

def coalesce_readings(rs):
    rs.sort()
    i=0
    while i<len(rs)-1:
        if rs[i].book == rs[i+1].book:
            joined = Reading(rs[i].book, rs[i].chap1, rs[i].verse1, rs[i+1].chapN, rs[i+1].verseN)
            if joined.length == rs[i].length + rs[i+1].length+1:
                joined.topics = rs[i].topics
                joined.kids = rs[i].kids
                joined.category = rs[i].category
                rs[i] = joined
                del rs[i+1]
            else:
                print('difference in length is', joined.length, 'versus', rs[i].length + rs[i+1].length)
                i=i+1
        else:
            i=i+1
    return rs

class Changes:
    """Changes made to the readings"""
    def __init__(self, error=None):
        self.error = error
        self.passages = []
        self.cut = []
        self.books = []

def modify_readings(passages, topics, kids):
    feedback = ''
    changes = Changes()
    passages = scriptures.extract(passages)
    for (book, chapter1, verse1, chapterN, verseN) in passages:
        r = Reading(book, chapter1, verse1, chapterN, verseN)
        r.kids = kids
        for t in topics:
            r.topics.add(t)
        for b in blocks:
            new_readings = set()
            old_readings = set()
            for rr in b.readings:
                if rr.book != r.book:
                    break
                if rr.overlaps(r):
                    old_readings.add(rr)
                    for rrr in rr-r:
                        new_readings.add(rrr)
                        changes.cut.append(rrr)
                    new_readings.add(r)
            if len(new_readings) > 0:
                changes.passages.append(r)
                for rr in old_readings:
                    b.readings.remove(rr)
                b.readings.extend(new_readings)
                b.readings.sort()
                changes.books.append(b)

    now = datetime.date.today()
    with open("schedule", "rb") as f:
        schedule = pickle.load(f)
    daynum = int((now - schedule[0]).total_seconds()/24/60/60)
    if len(schedule[1]) > daynum+1:
        for b in blocks:
            b.where_am_i = None
        del schedule[1][daynum+1:]
        with open("schedule", "wb") as f:
            pickle.dump(schedule, f)
    with open("readings", "wb") as f:
        pickle.dump(blocks, f)
    return changes
