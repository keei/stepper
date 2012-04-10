import surf

canonInD = ['d-1', 'a-1', 'b-1', 'f#1', 'g-1', 'd-1', 'g-1', 'a-1', 'd-1', 'a-1', 'b-1', 'f#1', 'g-1', 'd-1', 'g-1', 'a-1']

oscillator = surf.Oscillator()
oscillator.setOctaveOffset(2)

output = surf.Output()
output.setFilename('test.wav')
output.start()

sequencer = surf.Sequencer()
sequencer.setTempo(120)

for note in canonInD:
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
