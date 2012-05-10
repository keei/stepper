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

hihatOscillator = surf.NoiseGenerator()
hihatAttenuator = surf.Attenuator()

mixer = surf.Mixer()
mixer.setNumberOfChannels(3)
mixer.setVolume(2, 3) # Set third channel (channel 2) to 3/5ths volume
mixer.setPanning(0, -2.5) # Pan the lead left
mixer.setPanning(2, 2.5) # Pan the hi-hat right

output = surf.Output()
output.setFilename('walking_in_the_rain.wav')

sequencer = surf.Sequencer()
sequencer.loadSong('walking_in_the_rain.xml')

time = 0
trackLength = sequencer.getTrackLength()
sequencer.setPlaying(True)

while time < trackLength:
	time = sequencer.getTime()
	sequencer.incrementTime(surf.globalIncrementLengthInSeconds)

	leadCV1 = sequencer.getCV1InUnipolarVolts(0) # This can control anything.  Let's arbitrarily use it as the velocity.
	leadCV2 = sequencer.getCV2InUnipolarVolts(0)
	leadGate = sequencer.getGateInUnipolarVolts(0)
	leadPitch = sequencer.getPitchInUnipolarVolts(0)
	leadOscillator.setPitch(leadPitch)
	leadOscillator.setPulseWidth(leadCV2)
	leadOscillator.incrementTime(surf.globalIncrementLengthInSeconds)
	leadPulse = leadOscillator.getPulse()
	leadEnvelope.setGate(leadGate)
	leadEnvelope.incrementTime(surf.globalIncrementLengthInSeconds)
	leadAttenuator.setAudio(leadPulse)
	leadAttenuator.setCV1(leadEnvelope.getCV())
	leadAttenuator.setCV2(leadCV1)
	leadPulse = leadAttenuator.getAudio()

	bassCV1 = sequencer.getCV1InUnipolarVolts(1) # This can control anything.  Let's arbitrarily use it as the velocity.
	bassGate = sequencer.getGateInUnipolarVolts(1)
	bassPitch = sequencer.getPitchInUnipolarVolts(1)
	bassOscillator.setPitch(bassPitch)
	bassOscillator.incrementTime(surf.globalIncrementLengthInSeconds)
	bassPulse = bassOscillator.getPulse()
	bassEnvelope.setGate(bassGate)
	bassEnvelope.incrementTime(surf.globalIncrementLengthInSeconds)
	bassAttenuator.setAudio(bassPulse)
	bassAttenuator.setCV1(bassEnvelope.getCV())
	bassAttenuator.setCV2(bassCV1)
	bassPulse = bassAttenuator.getAudio()

	hihatCV1 = sequencer.getCV1InUnipolarVolts(2) # This can control anything.  Let's arbitrarily use it as the velocity.
	hihatGate = sequencer.getGateInUnipolarVolts(2)
	hihatNoise = hihatOscillator.getAudio()
	hihatAttenuator.setAudio(hihatNoise)
	hihatAttenuator.setCV1(hihatGate)
	hihatAttenuator.setCV2(hihatCV1)
	hihatNoise = hihatAttenuator.getAudio()

	mixer.setAudio(0, leadPulse)
	mixer.setAudio(1, bassPulse)
	mixer.setAudio(2, hihatNoise)

	mix = mixer.getAudio()

	output.setAudio(mix[0], mix[1])
	output.write()
