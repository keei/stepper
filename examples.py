import surf

canonInD = ['d-1', 'a-1', 'b-1', 'f#1', 'g-1', 'd-1', 'g-1', 'a-1', 'd-1', 'a-1', 'b-1', 'f#1', 'g-1', 'd-1', 'g-1', 'a-1']

oscillator = surf.Oscillator()

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

	currentNote = sequencer.getCurrentNote()
	cVNote = notationToCVConverter.convert(currentNote)
	oscillator.setPitch(cVNote)
	print(oscillator.frequency)
