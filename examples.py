import surf

canonInD = ['d1', 'a1', 'b1', 'fs1', 'g1', 'd1', 'g1', 'a1', 'd1', 'a1', 'b1', 'fs1', 'g1', 'd1', 'g1', 'a1']

output = surf.Output()
output.setFilename('test.wav')
output.start()

notationToCVConverter = surf.NotationToCVConverter()

sequencer = surf.Sequencer()
sequencer.setTempo(120)

for note in canonInD:
	sequencer.addNote(note)

time = 0
trackLength = sequencer.getTrackLength()

while time < trackLength:
	sequencer.incrementTime()
	time = sequencer.getTime()
	print(time)
	# currentNote = sequencer.getCurrentNote()
	# cVNote = notationToCVConverter.convert(currentNote)
	# print(cVNote)
