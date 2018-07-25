import pickle, lectionary, datetime

nt = lectionary.books['nt']

ot = lectionary.books['ot']

blocks = set()

NT_total = 0
for x in nt[4:]:
    b = lectionary.book_block(x, 'NT')
    blocks.add(b)
    print(b, len(b.readings), b.length)
    NT_total += b.length
    for r in b.readings:
        print('   ', r)

gospels_total = 0
for x in nt[:4]:
    b = lectionary.book_block(x, 'gospel')
    blocks.add(b)
    print(b, len(b.readings), b.length)
    gospels_total += b.length
    for r in b.readings:
        print('   ', r)

OT_total = 0
Psalms_total = 0
for x in ot:
    b = lectionary.book_block(x, 'OT')
    if b.name == 'Psalms':
        print('\n', b, b.length)
        for y in b.readings:
            n = str(y)
            bb = lectionary.Block(n[:n.find(':')].replace('Psalms', 'Psalm'), [y], 'Psalms')
            blocks.add(bb)
            print(bb, len(bb.readings), bb.length)
            Psalms_total += y.length
    else:
        blocks.add(b)
        print(b, len(b.readings), b.length)
        for r in b.readings:
            print('   ', r)
        OT_total += b.length

print('gospels:', gospels_total)
print('NT:', NT_total)
print('OT:', OT_total)
print('Psalms:', Psalms_total)

print('gospel daily goal', gospels_total/365.0)
print('NT daily goal', NT_total/365.0)
print('OT daily goal', OT_total/365.0/2)
print('Psalms daily goal', Psalms_total/365.0)

print(blocks)

today = datetime.date.today()

with open("readings", "wb") as f:
    pickle.dump(blocks, f)
with open("schedule", "wb") as f:
    pickle.dump((today, []), f)
