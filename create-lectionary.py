import pickle, lectionary

nt = lectionary.books['nt']

ot = lectionary.books['ot']

blocks = set()

NT_total = 0
for x in nt[4:]:
    b = lectionary.book_block(x)
    b.category = 'NT'
    blocks.add(b)
    print(b, len(b.readings), b.length)
    NT_total += b.length

gospels_total = 0
for x in nt[:4]:
    b = lectionary.book_block(x)
    b.category = 'gospel'
    blocks.add(b)
    print(b, len(b.readings), b.length)
    gospels_total += b.length

OT_total = 0
Psalms_total = 0
for x in ot:
    b = lectionary.book_block(x)
    b.category = 'OT'
    if b.name == 'Psalms':
        print('\n', b, b.length)
        for y in b.readings:
            n = str(y)
            bb = lectionary.Block(n[:n.find(':')].replace('Psalms', 'Psalm'), [y])
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
