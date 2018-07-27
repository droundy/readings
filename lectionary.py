from pysword.bible import SwordBible
import pickle, scriptures, random, datetime, copy, inspect, os

readingspath = os.path.dirname(inspect.getfile(inspect.currentframe()))
bible = SwordBible(readingspath+'/kjv',
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
        self.times_read = 0
    def __str__(self):
        return '{} ({})'.format(self.name, self.length)
    def __repr__(self):
        return self.name
    def __hash__(self):
        return hash(self.name)
    def next(self):
        for b in blocks:
            if self in b.readings:
                foundme = False
                for r in b.readings:
                    if foundme:
                        return r
                    if r == self:
                        foundme = True
                return None
        return None
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
        for rr in chunks:
            if r.kids:
                rr.kids = true
            rr.topics = copy.copy(r.topics)
            rr.category = rr.category
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

with open(readingspath+"/readings", "rb") as f:
    blocks = pickle.load(f)
    # The following is a workaround for old readings that did not get
    # constructed with times_read initialized.  Also for changes that
    # did not preserve the category of readings.
    for b in blocks:
        for r in b.readings:
            r.category = b.category
            if 'times_read' not in dir(r):
                r.times_read = 0

with open(readingspath+"/schedule", "rb") as f:
    schedule = pickle.load(f)

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

def get_all_readings():
    rs = []
    for b in blocks:
        rs.extend(b.readings)
    return rs

def get_all_kids():
    kids = [r for r in get_all_readings() if r.kids]
    least_times = min([r.times_read for r in kids])
    return list([r for r in kids if r.times_read == least_times])

def schedule_day():
    current_readings = {}
    priority = {}

    categories = ['NT', 'OT', 'Psalms']
    extra_kids = []
    for c in categories:
        current_readings[c] = []
        priority[c] = 0
    years = [1,2,1.5]

    num_days = len(schedule[1])

    for i in range(len(categories)):
        c = categories[i]
        total = sum([b.length for b in blocks if b.category == c])
        goal = total/365.0/years[i]
        print(c, 'daily goal', goal)
        have_read = sum([r.length for day in schedule[1] for r in day if r.category == c])
        print('    in', num_days, 'days have read', have_read)
        priority[c] = (num_days+1)*goal - have_read
        print('    priority', priority[c])
        for d in reversed(schedule[1]):
            for r in reversed(d):
                if r.category == c:
                    current_readings[c].append(r)
                    break
            if len(current_readings[c]) > 0:
                break

    print('most recently read', current_readings)
    next_readings = {}
    have_kids = False
    for c in categories:
        next_readings[c] = []
    for c in categories:
        for r in current_readings[c]:
            n = r.next()
            if n is not None:
                next_readings[c].append(n)
                have_kids = have_kids or n.kids
                priority[c] -= n.length
                n.times_read += 1
            else:
                for b in blocks:
                    if r in b.readings:
                        b.times_read += 1

    for x in range(2*len(categories)):
        c = max(priority, key=priority.get)
        if priority[c] < 0:
            break
        print('need', c, 'most')
        if len(next_readings[c]) == 0 or next_readings[c][-1].next() is None:
            if len(next_readings[c]) > 0:
                for b in blocks:
                    if next_readings[c][-1] in b.readings:
                        b.times_read += 1
            print('picking new', c, 'block')
            least_read = min([b.times_read for b in blocks if b.category == c])
            options = [b for b in blocks if b.category == c and b.times_read == least_read]
            b = random.choice(options)
            n = b.readings[0]
        else:
            n = next_readings[c][-1].next()
        if n.length > priority[c]:
            break
        next_readings[c].append(n)
        n.times_read += 1
        priority[c] -= n.length

    if not have_kids:
        all_kids = get_all_kids()
        n = random.choice(all_kids)
        n.times_read += 1
        extra_kids.append(n)
        print('new kid reading', n.name)
        priority[n.category] -= n.length

    today = []
    today.extend(extra_kids)
    for c in categories:
        today.extend(next_readings[c])
    print('>>>> current is', current_readings.values())
    print('>>>> today is', today)
    print('>>>> have_kids is', have_kids, extra_kids)
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
    daynum = int((now - schedule[0]).total_seconds()/24/60/60)
    if len(schedule[1]) > daynum+1:
        del schedule[1][daynum+1:]
        save_schedule()
    save_blocks()
    return changes

def save_schedule():
    with open(readingspath+"/schedule", "wb") as f:
            pickle.dump(schedule, f)
def save_blocks():
    with open(readingspath+"/readings", "wb") as f:
            pickle.dump(blocks, f)
