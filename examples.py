import surf

decay = surf.DecayEnvelopeGenerator()

attenuator = surf.Attenuator()

oscillator = surf.Oscillator()
oscillator.setOctaveOffset(2)

output = surf.Output()
output.setFilename('test.wav')

sequencer = surf.Sequencer()
sequencer.setTempo(120)

notation = open('walking_in_the_rain.txt')

for note in notation:
	sequencer.addNote(note)

time = 0
trackLength = sequencer.getTrackLength()

while time < trackLength:
	time = sequencer.getTime()
	increment = sequencer.incrementTime()
	cv1 = sequencer.getCV1() # This can control anything.  Let's arbitrarily use it as the velocity.
	gate = sequencer.getGate()
	pitch = sequencer.getPitch()
	oscillator.setPitch(pitch)
	oscillator.incrementTime(increment)
	pulse = oscillator.getPulse()
	decay.setGate(gate)
	decay.incrementTime(increment)
	attenuator.setAudio(pulse)
	attenuator.setCV1(decay.getCV())
	attenuator.setCV2(cv1)
	pulse = attenuator.getAudio()
	output.setValue(pulse)
	output.write()
