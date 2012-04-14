import surf

# 2012

leadEnvelope = surf.SustainReleaseEnvelopeGenerator()
leadEnvelope.setSpeed(0.025)

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

	leadCV1 = sequencer.getCV1(0)
	leadGate = sequencer.getGate(0)
	leadPitch = sequencer.getPitch(0)
	leadOscillator.setPitch(leadPitch)
	leadOscillator.incrementTime(increment)
	leadSaw = leadOscillator.getSawtooth()
	leadEnvelope.setGate(leadGate)
	leadEnvelope.incrementTime(increment)
	leadAttenuator.setAudio(leadSaw)
	leadAttenuator.setCV1(leadEnvelope.getCV())
	leadAttenuator.setCV2(leadCV1)
	leadSaw = leadAttenuator.getAudio()

	output.setValue(leadSaw)
	output.write()
