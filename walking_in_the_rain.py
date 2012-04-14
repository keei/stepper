import surf

# Walking In the Rain

leadEnvelope = surf.SustainReleaseEnvelopeGenerator()
leadEnvelope.setSpeed(0.025)

leadAttenuator = surf.Attenuator()

leadOscillator = surf.Oscillator()
leadOscillator.setOctaveOffset(2)

bassEnvelope = surf.SustainReleaseEnvelopeGenerator()
bassEnvelope.setSpeed(0.05)

bassAttenuator = surf.Attenuator()

bassOscillator = surf.Oscillator()
bassOscillator.setOctaveOffset(1)

hihatOscillator = surf.Oscillator()
hihatOscillator.setOctaveOffset(3)
hihatAttenuator = surf.Attenuator()

output = surf.Output()
output.setFilename('walking_in_the_rain.wav')

sequencer = surf.Sequencer()
sequencer.setTempo(120)

matrix = open('walking_in_the_rain.txt')

for eventRow in matrix:
	sequencer.addEventRow(eventRow)

time = 0
trackLength = sequencer.getTrackLength()

while time < trackLength:
	time = sequencer.getTime()
	increment = sequencer.incrementTime()

	leadCV1 = sequencer.getCV1(0) # This can control anything.  Let's arbitrarily use it as the velocity.
	leadCV2 = sequencer.getCV2(0)
	leadGate = sequencer.getGate(0)
	leadPitch = sequencer.getPitch(0)
	leadOscillator.setPitch(leadPitch)
	leadOscillator.setPulseWidth(leadCV2)
	leadOscillator.incrementTime(increment)
	leadPulse = leadOscillator.getPulse()
	leadEnvelope.setGate(leadGate)
	leadEnvelope.incrementTime(increment)
	leadAttenuator.setAudio(leadPulse)
	leadAttenuator.setCV1(leadEnvelope.getCV())
	leadAttenuator.setCV2(leadCV1)
	leadPulse = leadAttenuator.getAudio()

	bassCV1 = sequencer.getCV1(1) # This can control anything.  Let's arbitrarily use it as the velocity.
	bassGate = sequencer.getGate(1)
	bassPitch = sequencer.getPitch(1)
	bassOscillator.setPitch(bassPitch)
	bassOscillator.incrementTime(increment)
	bassPulse = bassOscillator.getPulse()
	bassEnvelope.setGate(bassGate)
	bassEnvelope.incrementTime(increment)
	bassAttenuator.setAudio(bassPulse)
	bassAttenuator.setCV1(bassEnvelope.getCV())
	bassAttenuator.setCV2(bassCV1)
	bassPulse = bassAttenuator.getAudio()

	hihatCV1 = sequencer.getCV1(2) # This can control anything.  Let's arbitrarily use it as the velocity.
	hihatGate = sequencer.getGate(2)
	hihatPitch = sequencer.getPitch(2)
	hihatOscillator.setPitch(hihatPitch)
	hihatOscillator.incrementTime(increment)
	hihatPulse = hihatOscillator.getPulse()
	hihatAttenuator.setAudio(hihatPulse)
	hihatAttenuator.setCV1(hihatGate)
	hihatAttenuator.setCV2(hihatCV1)
	hihatPulse = hihatAttenuator.getAudio()

	output.setValue(hihatPulse)
	output.write()