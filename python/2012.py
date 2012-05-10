import surf

# 2012

leadEnvelope = surf.SustainReleaseEnvelopeGenerator()
leadEnvelope.setSpeed(0.05)

leadAttenuator = surf.Attenuator()

leadOscillator = surf.Oscillator()
leadOscillator.setOctaveOffset(1)

output = surf.Output()
output.setFilename('2012.wav')

# These were the settings used to save the file
surf.DEFAULT_NUMBER_OF_ROWS = 16
surf.MAX_NUMBER_OF_PATTERNS = 16
surf.MAX_NUMBER_OF_ROWS = 16
surf.NUMBER_OF_CHANNELS = 1

sequencer = surf.Sequencer()
sequencer.loadPattern('2012.stepper3')
sequencer.setLoop(True)

time = 0
trackLength = sequencer.getTrackLength()
trackLength = trackLength * 4 # Loop through the tune 4 times
sequencer.setPlaying(True)

while time < trackLength:
	time = sequencer.getTime()
	sequencer.incrementTime(surf.globalIncrementLengthInSeconds)

	leadGate = sequencer.getGateInUnipolarVolts(0)
	leadPitch = sequencer.getPitchInUnipolarVolts(0)
	leadOscillator.setPitch(leadPitch)
	leadOscillator.incrementTime(surf.globalIncrementLengthInSeconds)
	leadSaw = leadOscillator.getSawtooth()
	leadEnvelope.setGate(leadGate)
	leadEnvelope.incrementTime(surf.globalIncrementLengthInSeconds)
	leadAttenuator.setAudio(leadSaw)
	leadAttenuator.setCV1(leadEnvelope.getCV())
	leadAttenuator.setCV2(5)
	leadSaw = leadAttenuator.getAudio()

	output.setAudio(leadSaw)
	output.write()
