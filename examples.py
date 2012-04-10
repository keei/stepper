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

stepLength = sequencer.getStepLength()
trackLength = sequencer.getTrackLength()

time = 0

while time < trackLength:
	time = time + stepLength
	print(time)
	# sequencer.setTime(time)
	# time = sequencer.getTime()
	# print(time)
	# sequencer.setTime(time)
	# currentNote = sequencer.getCurrentNote()
# for note in sequencer.notes:
	# cVNote = notationToCVConverter.convert(note)
	# print(cVNote)
