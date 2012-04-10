import surf

canonInD = ['D-1', 'A-1', 'B-1', 'F#1', 'G-1', 'D-1', 'G-1', 'A-1', 'D-1', 'A-1', 'B-1', 'F#1', 'G-1', 'D-1', 'G-1', 'A-1']

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
