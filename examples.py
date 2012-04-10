import surf

oscillator = surf.Oscillator()
oscillator.setOctaveOffset(2)

output = surf.Output()
output.setFilename('test.wav')
output.start()

sequencer = surf.Sequencer()
sequencer.setTempo(120)

notation = open('canon.txt')

for note in notation:
	sequencer.addNote(note)

time = 0
trackLength = sequencer.getTrackLength()

while time < trackLength:
	time = sequencer.getTime()
	increment = sequencer.incrementTime()
	pitch = sequencer.getPitch()
	oscillator.setPitch(pitch)
	oscillator.incrementTime(increment)
	waveform = oscillator.getSine()
	output.setValue(waveform)
	output.write()
