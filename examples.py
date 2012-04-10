import surf

canonInD = ['d1', 'a1', 'b1', 'fs1', 'g1', 'd1', 'g1', 'a1', 'd1', 'a1', 'b1', 'fs1', 'g1', 'd1', 'g1', 'a1']
notationToCVConverter = surf.NotationToCVConverter()

for note in canonInD:
	cVNote = notationToCVConverter.convert(note)
	print(cVNote)
