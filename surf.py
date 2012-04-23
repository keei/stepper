# Surf, version 0.1, for Python 3.
# By ZoeB, 2012.

# This is a software implementation of a basic modular synthesiser and
# sequencer.  Almost all values should be numbers between either -5 and
# +5, or 0 and +5.  Theoretically, it should be possible to connect this
# application to real modular hardware by converting these values into
# actual volts.

from math import ceil, floor, pi, sin
from random import uniform
from struct import pack
from wave import open

globalIncrementLengthInSeconds = 1.0 / 44100.0

class Attenuator:
	audioInBipolarVolts = 0.0
	cv1InBipolarVolts = 0.0
	cv2InBipolarVolts = 0.0

	def __init__(self):
		pass

	def getAudio(self):
		return self.audioInBipolarVolts / 25 * self.cv1InBipolarVolts * self.cv2InBipolarVolts

	def setAudio(self, audioInBipolarVolts):
		self.audioInBipolarVolts = audioInBipolarVolts
		return True

	def setCV1(self, cv1InBipolarVolts):
		self.cv1InBipolarVolts = cv1InBipolarVolts
		return True

	def setCV2(self, cv2InBipolarVolts):
		self.cv2InBipolarVolts = cv2InBipolarVolts
		return True

class DecayEnvelopeGenerator:
	cvInBipolarVolts = 0.0
	gateInUnipolarVolts = 0.0
	speedInUnipolarVolts = 0.1

	def __init__(self):
		self.gateInUnipolarVolts = 0.0
		self.speedInUnipolarVolts = 0.1

	def getCV(self):
		return self.cvInBipolarVolts

	def incrementTime(self, incrementLengthInSeconds):
		"""Update attributes to reflect the passing of the specified number of seconds."""
		if self.cvInBipolarVolts > 0:
			self.cvInBipolarVolts = self.cvInBipolarVolts - (incrementLengthInSeconds / self.speedInUnipolarVolts);

	def setGate(self, gateInUnipolarVolts):
		if self.gateInUnipolarVolts == 0 and gateInUnipolarVolts == 5:
			self.cvInBipolarVolts = 5
			self.gateInUnipolarVolts = 5
		else:
			self.gateInUnipolarVolts = gateInUnipolarVolts

	def setSpeed(self, speedInUnipolarVolts):
		self.speedInUnipolarVolts = speedInUnipolarVolts

class Inverter:
	audioInBipolarVolts = 0.0

	def __init__(self):
		pass

	def getAudio(self):
		return 0 - self.audioInBipolarVolts

	def setAudio(self, audioInBipolarVolts):
		self.audioInBipolarVolts = audioInBipolarVolts
		return True

class Mixer:
	audioInBipolarVolts = []
	numberOfChannels = 4
	panningInBipolarVolts = []
	volumeInUnipolarVolts = []

	def __init__(self):
		self.setNumberOfChannels(4) # Default to 4 channels

	def getAudio(self):
		audio = [0.0, 0.0]

		for channel in range(self.numberOfChannels):
			# Panning and volume are currently ignored.  I'll implement those later.
			audio[0] = audio[0] + (self.audioInBipolarVolts[channel] / self.numberOfChannels / 5 * self.volumeInUnipolarVolts[channel] / 10 * (10 - (self.panningInBipolarVolts[channel] + 5)))
			audio[1] = audio[1] + (self.audioInBipolarVolts[channel] / self.numberOfChannels / 5 * self.volumeInUnipolarVolts[channel] / 10 * (self.panningInBipolarVolts[channel] + 5))

		return audio

	def setAudio(self, channel, audioInBipolarVolts):
		self.audioInBipolarVolts[channel] = audioInBipolarVolts
		return True

	def setNumberOfChannels(self, numberOfChannels):
		self.audioInBipolarVolts = []
		self.panningInBipolarVolts = []
		self.volumeInUnipolarVolts = []

		for channel in range(numberOfChannels):
			self.audioInBipolarVolts.append(0.0)
			self.panningInBipolarVolts.append(0.0)
			self.volumeInUnipolarVolts.append(5.0)

		self.numberOfChannels = numberOfChannels
		return True

	def setPanning(self, channel, panningInBipolarVolts):
		self.panningInBipolarVolts[channel] = panningInBipolarVolts
		return True

	def setVolume(self, channel, volumeInUnipolarVolts):
		self.volumeInUnipolarVolts[channel] = volumeInUnipolarVolts
		return True

class NoiseGenerator:
	def __init__(self):
		pass

	def getAudio(self):
		return uniform(-5, 5)

class Oscillator:
	centOffsetInBipolarVolts = 0.0
	frequency = 0.0 # 0 to unlimited, float
	octaveOffsetInBipolarVolts = 0 # -5 to +5, int recommended
	pointerInUnipolarVolts = 0.0
	pulseWidthInBipolarVolts = 0.0
	sineWaveLookupTable = []

	def __init__(self):
		i = 0

		while i < 1000:
			self.sineWaveLookupTable.append(sin(i / 1000 * 2 * pi) * 5)
			i = i + 1

	def getPulse(self):
		if self.pointerInUnipolarVolts < self.pulseWidthInBipolarVolts:
			return 5
		else:
			return -5

	def getSine(self):
		pointer = int(floor((self.pointerInUnipolarVolts + 5) * 100))
		return self.sineWaveLookupTable[pointer]

	def getSawtooth(self):
		return self.pointerInUnipolarVolts

	def incrementTime(self, incrementLengthInSeconds):
		"""Update attributes to reflect the passing of the specified number of seconds."""
		self.pointerInUnipolarVolts = (self.pointerInUnipolarVolts + 5) / 10 # From [-5 to +5] to [0 to +1]
		self.pointerInUnipolarVolts = (self.pointerInUnipolarVolts + (self.frequency * incrementLengthInSeconds)) % 1
		self.pointerInUnipolarVolts = (self.pointerInUnipolarVolts * 10) - 5 # From [0 to +1] to [-5 to +5]

	def setOctaveOffset(self, octaveOffsetInBipolarVolts):
		self.octaveOffsetInBipolarVolts = octaveOffsetInBipolarVolts

	def setPitch(self, pitch):
		self.frequency = 440 / (2 ** 4.75) * (2 ** (pitch + self.octaveOffsetInBipolarVolts + (self.centOffsetInBipolarVolts / 5 * 100))) # A4 = 440Hz = 4.75v

	def setPulseWidth(self, pulseWidthInBipolarVolts):
		self.pulseWidthInBipolarVolts = pulseWidthInBipolarVolts

class Output:
	buffer = []
	filename = 'surf.wav'
	time = 0 # 0 to unlimited, int
	audioLeftInBipolarVolts = 0.0
	audioRightInBipolarVolts = 0.0
	writing = False

	def __del__(self):
		self.stop()

	def __init__(self):
		pass

	def setFilename(self, filename):
		self.filename = filename

	def setAudio(self, audioLeftInBipolarVolts, audioRightInBipolarVolts = None):
		self.audioLeftInBipolarVolts = audioLeftInBipolarVolts

		if audioRightInBipolarVolts != None:
			self.audioRightInBipolarVolts = audioRightInBipolarVolts
		else:
			self.audioRightInBipolarVolts = audioLeftInBipolarVolts

	def start(self):
		self.buffer = []
		self.writing = True

	def stop(self):
		# Only make CD quality files
		self.outputFile = open(self.filename, 'w')
		self.outputFile.setnchannels(2) # Stereo
		self.outputFile.setsampwidth(2) # 16-bit
		self.outputFile.setframerate(44100)

		audioBinary = bytes()
		audioBinary = audioBinary.join(self.buffer)
		self.outputFile.writeframes(audioBinary)

		self.outputFile.close()
		self.writing = False

	def write(self):
		if self.writing == False:
			self.start()

		audioLeft = int(floor(self.audioLeftInBipolarVolts / 5 * 32767)) # 16-bit
		audioBinary = pack('<h', audioLeft)
		self.buffer.append(audioBinary)
		audioRight = int(floor(self.audioRightInBipolarVolts / 5 * 32767)) # 16-bit
		audioBinary = pack('<h', audioRight)
		self.buffer.append(audioBinary)

class Sequencer:
	artistEmailAddress = ''
	artistName = ''
	averageEventRowLengthInSeconds = 0.0
	currentChannelNumber = 0
	currentEventRowNumber = 0
	currentPatternNumber = 0
	cv1InUnipolarVolts = []
	cv2InUnipolarVolts = []
	gateInUnipolarVolts = []
	loop = False
	noteTable = ['C-', 'C#', 'D-', 'D#', 'E-', 'F-', 'F#', 'G-', 'G#', 'A-', 'A#', 'B-']
	numberOfChannels = 4
	patternPositionInSeconds = 0.0
	patterns = []
	pitchInUnipolarVolts = []

	pitchVoltageLookupTable = {
		'C-1': 0.0,
		'C#1': 0.083,
		'D-1': 0.166,
		'D#1': 0.25,
		'E-1': 0.333,
		'F-1': 0.416,
		'F#1': 0.5,
		'G-1': 0.583,
		'G#1': 0.666,
		'A-1': 0.75,
		'A#1': 0.833,
		'B-1': 0.916,
		'C-2': 1.0,
		'C#2': 1.083,
		'D-2': 1.166,
		'D#2': 1.25,
		'E-2': 1.333,
		'F-2': 1.416,
		'F#2': 1.5,
		'G-2': 1.583,
		'G#2': 1.666,
		'A-2': 1.75,
		'A#2': 1.833,
		'B-2': 1.916,
		'C-3': 2.0,
		'C#3': 2.083,
		'D-3': 2.166,
		'D#3': 2.25,
		'E-3': 2.333,
		'F-3': 2.416,
		'F#3': 2.5,
		'G-3': 2.583,
		'G#3': 2.666,
		'A-3': 2.75,
		'A#3': 2.833,
		'B-3': 2.916,
		'C-4': 3.0,
		'C#4': 3.083,
		'D-4': 3.166,
		'D#4': 3.25,
		'E-4': 3.333,
		'F-4': 3.416,
		'F#4': 3.5,
		'G-4': 3.583,
		'G#4': 3.666,
		'A-4': 3.75,
		'A#4': 3.833,
		'B-4': 3.916,
		'C-5': 4.0,
		'C#5': 4.083,
		'D-5': 4.166,
		'D#5': 4.25,
		'E-5': 4.333,
		'F-5': 4.416,
		'F#5': 4.5,
		'G-5': 4.583,
		'G#5': 4.666,
		'A-5': 4.75,
		'A#5': 4.833,
		'B-5': 4.916,
		'C-6': 5.0
	}

	playing = False
	songInformation = ''
	songName = ''
	swingInBipolarVolts = 0.0
	tempo = 120.0
	timeInSeconds = 0.0

	def __init__(self):
		self.setTempo(120) # Default to 120BPM
		self.setNumberOfChannels(4) # Default to 4 channels
		self.addPattern() # Add the first pattern, pattern 0

	def addEventRow(self, eventRow):
		"""Load in values for all channels simultaneously."""
		if not self.patterns[self.currentPatternNumber]:
			self.setNumberOfChannels(ceil(len(eventRow) / 16))

		self.patterns[self.currentPatternNumber].append(eventRow)

	def addPattern(self):
		self.patterns.append([])

	def decrementCurrentChannelNumber(self):
		if self.currentChannelNumber > 0:
			self.currentChannelNumber = self.currentChannelNumber - 1

	def decrementCurrentEventRowNumber(self):
		if self.currentEventRowNumber > 0:
			self.currentEventRowNumber = self.currentEventRowNumber - 1
			# self.patternPositionInSeconds should update accordingly, taking swing into account.

	def decrementCurrentPatternNumber(self):
		if self.currentPatternNumber > 0:
			self.currentPatternNumber = self.currentPatternNumber - 1

	def getArtistEmailAddress(self, artistEmailAddress):
		return self.artistEmailAddress

	def getArtistName(self, artistName):
		return self.artistName

	def getCurrentChannelNumber(self):
		return self.currentChannelNumber

	def getCurrentEventRowNumber(self):
		return self.currentEventRowNumber

	def getCurrentPatternNumber(self):
		return self.currentPatternNumber

	def getCV1(self, channel):
		return self.cv1InUnipolarVolts[channel]

	def getCV2(self, channel):
		return self.cv2InUnipolarVolts[channel]

	def getGate(self, channel):
		return self.gateInUnipolarVolts[channel]

	def getLoopTime(self):
		return self.patternPositionInSeconds

	def getPatternLength(self):
		return len(self.patterns[self.currentPatternNumber])

	def getPitch(self, channel):
		return self.pitchInUnipolarVolts[channel]

	def getPlaying(self):
		return self.playing

	def getSongInformation(self, songInformation):
		return self.songInformation

	def getSongName(self, songName):
		return self.songName

	def getSwing(self):
		return self.swingInBipolarVolts

	def getTrackLength(self):
		return len(self.patterns[self.currentPatternNumber]) * self.averageEventRowLengthInSeconds # This is now grossly oversimplifying, for only having one pattern!

	def getTime(self):
		return self.timeInSeconds

	def incrementCurrentChannelNumber(self):
		if self.currentChannelNumber < self.numberOfChannels - 1:
			self.currentChannelNumber = self.currentChannelNumber + 1

	def incrementCurrentEventRowNumber(self):
		if self.currentEventRowNumber < len(self.patterns[self.currentPatternNumber]) - 1:
			self.currentEventRowNumber = self.currentEventRowNumber + 1
			# self.patternPositionInSeconds should update accordingly, taking swing into account.

	def incrementCurrentPatternNumber(self):
		if self.currentPatternNumber < len(self.patterns) - 1:
			self.currentPatternNumber = self.currentPatternNumber + 1

	def incrementTime(self, incrementLengthInSeconds):
		if self.playing == False:
			return

		self.timeInSeconds = self.timeInSeconds + incrementLengthInSeconds
		self.patternPositionInSeconds = self.patternPositionInSeconds + incrementLengthInSeconds
		eventRowPairLengthInSeconds = self.averageEventRowLengthInSeconds * 2

		# Work out the current event row
		eventRowPairNumber = int(self.patternPositionInSeconds // eventRowPairLengthInSeconds)
		currentEventRowNumber = eventRowPairNumber * 2

		swingAsDecimal = (self.swingInBipolarVolts + 5.0) / 10.0
		firstEventRowLengthInSeconds = self.averageEventRowLengthInSeconds / 0.5 * swingAsDecimal
		eventRowPairPositionInSeconds = self.patternPositionInSeconds - (eventRowPairLengthInSeconds * eventRowPairNumber)

		if eventRowPairPositionInSeconds > firstEventRowLengthInSeconds:
			currentEventRowNumber = currentEventRowNumber + 1
			eventRowLengthInSeconds = eventRowPairLengthInSeconds - firstEventRowLengthInSeconds
			eventRowPositionInSeconds = eventRowPairPositionInSeconds - firstEventRowLengthInSeconds
		else:
			eventRowLengthInSeconds = firstEventRowLengthInSeconds
			eventRowPositionInSeconds = eventRowPairPositionInSeconds

		if currentEventRowNumber > len(self.patterns[self.currentPatternNumber]) - 1:
			if self.loop == True:
				self.patternPositionInSeconds = 0.0
				# Do NOT increment self.timeInSeconds, that's the absolute time the sequencer's been running!

				# It doesn't look like we can continue on to the next iteration of the loop, so let's just reset everything to 0 instead, which is what would happen anyway.
				currentEventRowNumber = 0
				eventRowPairNumber = 0
				eventRowPairPositionInSeconds = 0.0
				eventRowPositionInSeconds = 0.0
			else:
				currentEventRowNumber = len(self.patterns[self.currentPatternNumber]) - 1

		self.currentEventRowNumber = currentEventRowNumber

		# Read in the current and next event rows
		eventRow = self.patterns[self.currentPatternNumber][currentEventRowNumber]
		nextEventRowNumber = currentEventRowNumber + 1

		if nextEventRowNumber > len(self.patterns[self.currentPatternNumber]) - 1:
			nextEventRowNumber = len(self.patterns[self.currentPatternNumber]) - 1

		nextEventRow = self.patterns[self.currentPatternNumber][nextEventRowNumber]

		# Work out each current event's pitch, slide or lack thereof, gate length, CV1 and CV2
		for channel in range(self.numberOfChannels):
			# Convert the pitch to a control voltage, 1v/oct
			pitchName = eventRow[(channel * 16) + 0:(channel * 16) + 3]

			if pitchName != '...':
				self.pitchInUnipolarVolts[channel] = self.pitchVoltageLookupTable[pitchName]

			# Slide if necessary
			if eventRow[(channel * 16) + 4:(channel * 16) + 5] == 'S':
				slide = True
			else:
				slide = False

			# Set the gate length
			if eventRow[(channel * 16) + 6:(channel * 16) + 8] != '..':
				gateLengthInSeconds = float(eventRow[(channel * 16) + 6:(channel * 16) + 8]) / float(99) * float(eventRowLengthInSeconds)
			elif slide == True:
				gateLengthInSeconds = eventRowLengthInSeconds
			elif eventRow[(channel * 16) + 0:(channel * 16) + 3] != '...':
				gateLengthInSeconds = eventRowLengthInSeconds / 2
			else:
				gateLengthInSeconds = 0.0

			# We need to make sure that we don't get any stray gate ons or gate offs, even for one single iteration
			if eventRowPositionInSeconds > gateLengthInSeconds or (eventRowPositionInSeconds == gateLengthInSeconds and gateLengthInSeconds == 0):
				self.gateInUnipolarVolts[channel] = 0.0
			else:
				self.gateInUnipolarVolts[channel] = 5.0

			# Set CV1
			eventCV1 = eventRow[(channel * 16) + 9:(channel * 16) + 11]

			if eventCV1 != '..':
				self.cv1InUnipolarVolts[channel] = float(eventCV1) / float(99) * float(5)

			# Set CV2
			eventCV2 = eventRow[(channel * 16) + 12:(channel * 16) + 14]

			if eventCV2 != '..':
				self.cv2InUnipolarVolts[channel] = float(eventCV2) / float(99) * float(5)

			# Do the actual sliding
			if slide == True:
				nextPitchName = nextEventRow[(channel * 16) + 0:(channel * 16) + 3]

				if nextPitchName != '...':
					nextPitchInUnipolarVolts = self.pitchVoltageLookupTable[nextPitchName]
				else:
					nextPitchInUnipolarVolts = self.pitchInUnipolarVolts[channel]

				nextEventCV1 = nextEventRow[(channel * 16) + 9:(channel * 16) + 11]

				if nextEventCV1 != '..':
					nextCV1InUnipolarVolts = float(nextEventCV1) / float(99) * float(5)
				else:
					nextCV1InUnipolarVolts = self.cv1InUnipolarVolts[channel]

				nextEventCV2 = nextEventRow[(channel * 16) + 12:(channel * 16) + 14]

				if nextEventCV2 != '..':
					nextCV2InUnipolarVolts = float(nextEventCV2) / float(99) * float(5)
				else:
					nextCV2InUnipolarVolts = self.cv2InUnipolarVolts[channel]

				# Glide effortlessly and gracefully from self.pitchInUnipolarVolts to nextPitchInUnipolarVolts
				if eventRowPositionInSeconds > eventRowLengthInSeconds / 2:
					pitchDifference = nextPitchInUnipolarVolts - self.pitchInUnipolarVolts[channel]
					cv1Difference = nextCV1InUnipolarVolts - self.cv1InUnipolarVolts[channel]
					cv2Difference = nextCV2InUnipolarVolts - self.cv2InUnipolarVolts[channel]

					# Work out how far along the slide we are, from 0 to 1
					beginningInSeconds = eventRowLengthInSeconds / 2
					endInSeconds = eventRowLengthInSeconds
					positionInSeconds = eventRowPositionInSeconds
					offsetPositionInSeconds = positionInSeconds - beginningInSeconds
					offsetEndInSeconds = endInSeconds - beginningInSeconds
					positionAsDecimal = offsetPositionInSeconds / offsetEndInSeconds

					self.pitchInUnipolarVolts[channel] = self.pitchInUnipolarVolts[channel] + (pitchDifference / 1 * positionAsDecimal)
					self.cv1InUnipolarVolts[channel] = self.cv1InUnipolarVolts[channel] + (cv1Difference / 1 * positionAsDecimal)
					self.cv2InUnipolarVolts[channel] = self.cv2InUnipolarVolts[channel] + (cv2Difference / 1 * positionAsDecimal)

		return incrementLengthInSeconds

	def removeEventRow(self):
		"""Remove the last value for all channels."""
		self.patterns[self.currentPatternNumber].pop()

	def setArtistEmailAddress(self, artistEmailAddress):
		self.artistEmailAddress = artistEmailAddress

	def setArtistName(self, artistName):
		self.artistName = artistName

	def setLoop(self, loop):
		self.loop = loop

	def setNumberOfChannels(self, numberOfChannels):
		self.cv1InUnipolarVolts = []
		self.cv2InUnipolarVolts = []
		self.gateInUnipolarVolts = []
		self.pitchInUnipolarVolts = []

		for channel in range(numberOfChannels):
			self.cv1InUnipolarVolts.append(0.0)
			self.cv2InUnipolarVolts.append(0.0)
			self.gateInUnipolarVolts.append(0.0)
			self.pitchInUnipolarVolts.append(0.0)

		self.numberOfChannels = numberOfChannels
		return True

	def setPlaying(self, playing):
		self.playing = playing

	def setSongInformation(self, songInformation):
		self.songInformation = songInformation

	def setSongName(self, songName):
		self.songName = songName

	def setSwing(self, swingInBipolarVolts):
		self.swingInBipolarVolts = swingInBipolarVolts

	def setTempo(self, tempo):
		self.tempo = float(tempo)
		crotchetLengthInSeconds = 60.0 / self.tempo
		semiquaverLengthInSeconds = crotchetLengthInSeconds / 4.0
		self.averageEventRowLengthInSeconds = semiquaverLengthInSeconds

class SustainReleaseEnvelopeGenerator:
	cvInUnipolarVolts = 0.0
	gateInUnipolarVolts = 0.0
	speedInUnipolarVolts = 0.1

	def __init__(self):
		self.gateInUnipolarVolts = 0.0
		self.speedInUnipolarVolts = 0.1

	def getCV(self):
		return self.cvInUnipolarVolts

	def incrementTime(self, incrementLengthInSeconds):
		"""Update attributes to reflect the passing of the specified number of seconds."""
		if self.cvInUnipolarVolts > 0 and self.gateInUnipolarVolts == 0:
			self.cvInUnipolarVolts = self.cvInUnipolarVolts - (incrementLengthInSeconds / self.speedInUnipolarVolts);

	def setGate(self, gateInUnipolarVolts):
			self.gateInUnipolarVolts = gateInUnipolarVolts

			if gateInUnipolarVolts == 5:
				self.cvInUnipolarVolts = gateInUnipolarVolts

	def setSpeed(self, speedInUnipolarVolts):
		self.speedInUnipolarVolts = speedInUnipolarVolts
