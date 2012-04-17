import surf

# 2012

leadEnvelope = surf.SustainReleaseEnvelopeGenerator()
leadEnvelope.setSpeed(0.05)

leadAttenuator = surf.Attenuator()

leadOscillator = surf.Oscillator()
leadOscillator.setOctaveOffset(1)

output = surf.Output()
output.setFilename('2012.wav')

sequencer = surf.Sequencer()
sequencer.setTempo(118)

matrix = open('2012.txt')

for eventRow in matrix:
	sequencer.addEventRow(eventRow)

time = 0
trackLength = sequencer.getTrackLength()

while time < trackLength:
	time = sequencer.getTime()
	increment = sequencer.incrementTime()

	leadGate = sequencer.getGate(0)
	leadPitch = sequencer.getPitch(0)
	leadOscillator.setPitch(leadPitch)
	leadOscillator.incrementTime(increment)
	leadSaw = leadOscillator.getSawtooth()
	leadEnvelope.setGate(leadGate)
	leadEnvelope.incrementTime(increment)
	leadAttenuator.setAudio(leadSaw)
	leadAttenuator.setCV1(leadEnvelope.getCV())
	leadAttenuator.setCV2(5)
	leadSaw = leadAttenuator.getAudio()

	output.setAudio(leadSaw)
	output.write()
