import surf

canonInD = ['d1', 'a1', 'b1', 'fs1', 'g1', 'd1', 'g1', 'a1', 'd1', 'a1', 'b1', 'fs1', 'g1', 'd1', 'g1', 'a1']

output = surf.Output()
output.setFilename('test.wav')
output.start()

notationToCVConverter = surf.NotationToCVConverter()

sequencer = surf.Sequencer()
sequencer.setTempo(120)

for note in canonInD:
	sequencer.pushNote(note)

trackLength = sequencer.getTrackLength()

for sample in range (trackLength):
	pass
# for note in sequencer.notes:
	# cVNote = notationToCVConverter.convert(note)
	# print(cVNote)
