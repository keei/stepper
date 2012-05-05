# Surf, version 0.1, for Python 3.  # By ZoeB, 2012.

# This is a software implementation of a basic modular synthesiser and
# sequencer.  Almost all values should be numbers between either -5 and
# +5, or 0 and +5.  Theoretically, it should be possible to connect this
# application to real modular hardware by converting these values into
# actual volts.

from xml.etree import ElementTree
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
			self.cvInBipolarVolts = self.cvInBipolarVolts - (incrementLengthInSeconds / self.speedInUnipolarVolts)

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
	averageRowLengthInSeconds = 0.0
	currentChannelNumber = 0
	currentRowNumber = 0
	currentPatternNumber = 0
	cv1InCents = []
	cv1InCentsAndDots = []
	cv1InUnipolarVolts = []
	cv2InCents = []
	cv2InCentsAndDots = []
	cv2InUnipolarVolts = []
	gateInCents = []
	gateInCentsAndDots = []
	gateInUnipolarVolts = []
	loop = False
	noteTable = ['C-', 'C#', 'D-', 'D#', 'E-', 'F-', 'F#', 'G-', 'G#', 'A-', 'A#', 'B-']
	numberOfChannels = 4
	patternPositionInSeconds = 0.0
	patternsInCents = []
	patternsInCentsAndDots = []
	pitchInChars = []
	pitchInCharsAndDots = []
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

	def addPattern(self):
		self.patternsInCents.append([])
		self.patternsInCentsAndDots.append([])

	def decrementCurrentChannelNumber(self):
		if self.currentChannelNumber > 0:
			self.currentChannelNumber = self.currentChannelNumber - 1

	def decrementCurrentRowNumber(self):
		if self.currentRowNumber > 0:
			self.currentRowNumber = self.currentRowNumber - 1

	def decrementCurrentPatternNumber(self):
		if self.currentPatternNumber > 0:
			self.currentPatternNumber = self.currentPatternNumber - 1

	def getArtistEmailAddress(self, artistEmailAddress):
		return self.artistEmailAddress

	def getArtistName(self, artistName):
		return self.artistName

	def getCurrentChannelNumber(self):
		return self.currentChannelNumber

	def getCurrentRowNumber(self):
		return self.currentRowNumber

	def getCurrentPatternNumber(self):
		return self.currentPatternNumber

	def getCV1InCents(self, channel):
		return self.cv1InCents[channel]

	def getCV1InCentsAndDots(self, channel):
		return self.cv1InCentsAndDots[channel]

	def getCV1Output(self, channel):
		return self.cv1InUnipolarVolts[channel]

	def getCV2InCents(self, channel):
		return self.cv2InCents[channel]

	def getCV2InCentsAndDots(self, channel):
		return self.cv2InCentsAndDots[channel]

	def getCV2Output(self, channel):
		return self.cv2InUnipolarVolts[channel]

	def getGateInCents(self, channel):
		return self.gateInCents[channel]

	def getGateInCentsAndDots(self, channel):
		return self.gateInCentsAndDots[channel]

	def getGateOutput(self, channel):
		return self.gateInUnipolarVolts[channel]

	def getLoopTime(self):
		return self.patternPositionInSeconds

	def getOctave(self):
		return self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['pitch'][2:]

	def getPatternLength(self):
		return len(self.patternsInCentsAndDots[self.currentPatternNumber])

	def getPitchOutput(self, channel):
		return self.pitchInUnipolarVolts[channel]

	def getPitchInCharsAndDots(self, channel):
		return self.pitchInCharsAndDots[channel]

	def getPlaying(self):
		return self.playing

	def getSemitone(self):
		return self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['pitch'][:2]

	def getSlide(self):
		return self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['slide']

	def getSongInformation(self, songInformation):
		return self.songInformation

	def getSongName(self, songName):
		return self.songName

	def getSwing(self):
		return self.swingInBipolarVolts

	def getTrackLength(self):
		return len(self.patternsInCentsAndDots[self.currentPatternNumber]) * self.averageRowLengthInSeconds # This is now grossly oversimplifying, for only having one pattern!

	def getTime(self):
		return self.timeInSeconds

	def incrementCurrentChannelNumber(self):
		if self.currentChannelNumber < self.numberOfChannels - 1:
			self.currentChannelNumber = self.currentChannelNumber + 1

	def incrementCurrentRowNumber(self):
		if self.currentRowNumber < len(self.patternsInCentsAndDots[self.currentPatternNumber]) - 1:
			self.currentRowNumber = self.currentRowNumber + 1

	def incrementCurrentPatternNumber(self):
		if self.currentPatternNumber < len(self.patternsInCentsAndDots) - 1:
			self.currentPatternNumber = self.currentPatternNumber + 1

	def incrementTime(self, incrementLengthInSeconds):
		if self.playing == False:
			return

		self.timeInSeconds = self.timeInSeconds + incrementLengthInSeconds
		self.patternPositionInSeconds = self.patternPositionInSeconds + incrementLengthInSeconds
		rowPairLengthInSeconds = self.averageRowLengthInSeconds * 2

		# Work out the current event row
		rowPairNumber = int(self.patternPositionInSeconds // rowPairLengthInSeconds)
		currentRowNumber = rowPairNumber * 2

		swingAsDecimal = (self.swingInBipolarVolts + 5.0) / 10.0
		firstRowLengthInSeconds = self.averageRowLengthInSeconds / 0.5 * swingAsDecimal
		rowPairPositionInSeconds = self.patternPositionInSeconds - (rowPairLengthInSeconds * rowPairNumber)

		if rowPairPositionInSeconds > firstRowLengthInSeconds:
			currentRowNumber = currentRowNumber + 1
			rowLengthInSeconds = rowPairLengthInSeconds - firstRowLengthInSeconds
			rowPositionInSeconds = rowPairPositionInSeconds - firstRowLengthInSeconds
		else:
			rowLengthInSeconds = firstRowLengthInSeconds
			rowPositionInSeconds = rowPairPositionInSeconds

		if currentRowNumber > len(self.patternsInCentsAndDots[self.currentPatternNumber]) - 1:
			if self.loop == True:
				self.patternPositionInSeconds = 0.0
				# Do NOT increment self.timeInSeconds, that's the absolute time the sequencer's been running!

				# It doesn't look like we can continue on to the next iteration of the loop, so let's just reset everything to 0 instead, which is what would happen anyway.
				currentRowNumber = 0
				rowPairNumber = 0
				rowPairPositionInSeconds = 0.0
				rowPositionInSeconds = 0.0
			else:
				currentRowNumber = len(self.patternsInCentsAndDots[self.currentPatternNumber]) - 1

		self.currentRowNumber = currentRowNumber

		# Read in the current and next event rows
		nextRowNumber = currentRowNumber + 1

		if nextRowNumber > len(self.patternsInCentsAndDots[self.currentPatternNumber]) - 1:
			nextRowNumber = len(self.patternsInCentsAndDots[self.currentPatternNumber]) - 1

		# Work out each current event's pitch, slide or lack thereof, gate length, CV1 and CV2
		for channel in range(self.numberOfChannels):
			# Convert the pitch to a control voltage, 1v/oct
			self.pitchInCharsAndDots[channel] = self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][channel]['pitch']

			if self.pitchInCharsAndDots[channel] != '...':
				self.pitchInChars[channel] = self.pitchInCharsAndDots[channel]
				self.pitchInUnipolarVolts[channel] = self.pitchVoltageLookupTable[self.pitchInCharsAndDots[channel]]

			# Slide if necessary
			slide = self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][channel]['slide']

			# Set the gate length
			self.gateInCentsAndDots[channel] = self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][channel]['gate']

			if self.gateInCentsAndDots[channel] != '..':
				self.gateInCents[channel] = self.gateInCentsAndDots[channel]
			elif slide == True:
				self.gateInCents[channel] = 99
				gateLengthInSeconds = rowLengthInSeconds
			elif self.pitchInCharsAndDots[channel] != '...':
				self.gateInCents[channel] = 50 # Really, it should be 49.5
			else:
				self.gateInCents[channel] = 0

			gateLengthInSeconds = float(self.gateInCents[channel]) / float(99) * float(rowLengthInSeconds)

			# We need to make sure that we don't get any stray gate ons or gate offs, even for one single iteration
			if rowPositionInSeconds > gateLengthInSeconds or (rowPositionInSeconds == gateLengthInSeconds and gateLengthInSeconds == 0):
				self.gateInUnipolarVolts[channel] = 0.0
			else:
				self.gateInUnipolarVolts[channel] = 5.0

			# Set CV1
			self.cv1InCentsAndDots[channel] = self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][channel]['cv1']

			if self.cv1InCentsAndDots[channel] != '..':
				self.cv1InCents[channel] = self.cv1InCentsAndDots[channel]
				self.cv1InUnipolarVolts[channel] = float(self.cv1InCents[channel]) / float(99) * float(5)

			# Set CV2
			self.cv2InCentsAndDots[channel] = self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][channel]['cv2']

			if self.cv2InCentsAndDots[channel] != '..':
				self.cv2InCents[channel] = self.cv2InCentsAndDots[channel]
				self.cv2InUnipolarVolts[channel] = float(self.cv2InCents[channel]) / float(99) * float(5)

			# Do the actual sliding
			if slide == True:
				nextPitchName = self.patternsInCentsAndDots[self.currentPatternNumber][nextRowNumber][channel]['pitch']

				if nextPitchName != '...':
					nextPitchInUnipolarVolts = self.pitchVoltageLookupTable[nextPitchName]
				else:
					nextPitchInUnipolarVolts = self.pitchInUnipolarVolts[channel]

				nextEventCV1 = self.patternsInCentsAndDots[self.currentPatternNumber][nextRowNumber][channel]['cv1']

				if nextEventCV1 != '..':
					nextCV1InUnipolarVolts = float(nextEventCV1) / float(99) * float(5)
				else:
					nextCV1InUnipolarVolts = self.cv1InUnipolarVolts[channel]

				nextEventCV2 = self.patternsInCentsAndDots[self.currentPatternNumber][nextRowNumber][channel]['cv2']

				if nextEventCV2 != '..':
					nextCV2InUnipolarVolts = float(nextEventCV2) / float(99) * float(5)
				else:
					nextCV2InUnipolarVolts = self.cv2InUnipolarVolts[channel]

				# Glide effortlessly and gracefully from self.pitchInUnipolarVolts to nextPitchInUnipolarVolts
				if rowPositionInSeconds > rowLengthInSeconds / 2:
					pitchDifference = nextPitchInUnipolarVolts - self.pitchInUnipolarVolts[channel]
					cv1Difference = nextCV1InUnipolarVolts - self.cv1InUnipolarVolts[channel]
					cv2Difference = nextCV2InUnipolarVolts - self.cv2InUnipolarVolts[channel]

					# Work out how far along the slide we are, from 0 to 1
					beginningInSeconds = rowLengthInSeconds / 2
					endInSeconds = rowLengthInSeconds
					positionInSeconds = rowPositionInSeconds
					offsetPositionInSeconds = positionInSeconds - beginningInSeconds
					offsetEndInSeconds = endInSeconds - beginningInSeconds
					positionAsDecimal = offsetPositionInSeconds / offsetEndInSeconds

					self.pitchInUnipolarVolts[channel] = self.pitchInUnipolarVolts[channel] + (pitchDifference / 1 * positionAsDecimal)
					self.cv1InUnipolarVolts[channel] = self.cv1InUnipolarVolts[channel] + (cv1Difference / 1 * positionAsDecimal)
					self.cv2InUnipolarVolts[channel] = self.cv2InUnipolarVolts[channel] + (cv2Difference / 1 * positionAsDecimal)

		return incrementLengthInSeconds

	def loadSong(self, filename):
		self.patternsInCentsAndDots = []
		xmlSong = ElementTree.ElementTree()
		xmlSong.parse(filename)
		self.songName = xmlSong.find('name').text
		self.artistName = xmlSong.find('artist-name').text
		self.artistEmailAddress = xmlSong.find('artist-email-address').text
		self.songInformation = xmlSong.find('information').text
		self.songTempo = float(xmlSong.find('tempo').text) # Internally stored as a float so that division works with it.  In XML song files, it's a string pretending to be an int.
		patternsInCentsAndDots = list(xmlSong.iter('pattern'))

		for pattern in patternsInCentsAndDots:
			self.patternsInCentsAndDots.append([])
			patternNumber = int(pattern.attrib['number'])
			rows = list(pattern.iter('row'))

			for row in rows:
				self.patternsInCentsAndDots[patternNumber - 1].append([])
				rowNumber = int(row.attrib['number'])
				channels = list(row.iter('channel'))

				for channel in channels:
					self.patternsInCentsAndDots[patternNumber - 1][rowNumber - 1].append([])
					channelNumber = int(channel.attrib['number'])

					pitchInCharsAndDots = channel.find('pitch').text
					slide = channel.find('slide').text
					gate = channel.find('gate').text
					cv1 = channel.find('cv1').text
					cv2 = channel.find('cv2').text

					if not pitchInCharsAndDots:
						pitchInCharsAndDots = '...'

					if slide == 'true':
						slide = True
					else:
						slide = False

					if not gate:
						gate = '..'

					if not cv1:
						cv1 = '..'

					if not cv2:
						cv2 = '..'

					self.patternsInCentsAndDots[patternNumber - 1][rowNumber - 1][channelNumber - 1] = {'pitch': pitchInCharsAndDots, 'slide': slide, 'gate': gate, 'cv1': cv1, 'cv2': cv2}

		self.numberOfChannels = channelNumber

	def removeRow(self):
		"""Remove the last value for all channels."""
		self.patternsInCentsAndDots[self.currentPatternNumber].pop()

	def saveSong(self, filename):
		xmlSong = ElementTree.Element('song')

		xmlName = ElementTree.SubElement(xmlSong, 'name')
		xmlName.text = self.songName

		xmlArtistName = ElementTree.SubElement(xmlSong, 'artist-name')
		xmlArtistName.text = self.artistName

		xmlArtistEmailAddress = ElementTree.SubElement(xmlSong, 'artist-email-address')
		xmlArtistEmailAddress.text = self.artistEmailAddress

		xmlSongInformation = ElementTree.SubElement(xmlSong, 'information')
		xmlSongInformation.text = self.songInformation

		xmlTempo = ElementTree.SubElement(xmlSong, 'tempo')
		xmlTempo.text = str(int(self.tempo))

		xmlPatterns = ElementTree.SubElement(xmlSong, 'patternsInCentsAndDots')
		patternNumber = 0

		for pattern in self.patternsInCentsAndDots:
			patternNumber = patternNumber + 1
			xmlPattern = ElementTree.SubElement(xmlPatterns, 'pattern')
			xmlPattern.attrib = {'number': str(patternNumber)}
			rowNumber = 0

			for row in pattern:
				rowNumber = rowNumber + 1
				xmlRow = ElementTree.SubElement(xmlPattern, 'row')
				xmlRow.attrib = {'number': str(rowNumber)}
				channelNumber = 0

				for channel in row:
					channelNumber = channelNumber + 1
					xmlChannel = ElementTree.SubElement(xmlRow, 'channel')
					xmlChannel.attrib = {'number': str(channelNumber)}

					xmlPitch = ElementTree.SubElement(xmlChannel, 'pitch')

					if channel['pitch'] != '...':
						xmlPitch.text = channel['pitch']

					xmlSlide = ElementTree.SubElement(xmlChannel, 'slide')

					if channel['slide'] == True:
						xmlSlide.text = 'true'
					# else:
						# xmlSlide.text = 'false'

					xmlGate = ElementTree.SubElement(xmlChannel, 'gate')

					if channel['gate'] != '..':
						xmlGate.text = channel['gate']

					xmlCV1 = ElementTree.SubElement(xmlChannel, 'cv1')

					if channel['cv1'] != '..':
						xmlCV1.text = channel['cv1']

					xmlCV2 = ElementTree.SubElement(xmlChannel, 'cv2')

					if channel['cv2'] != '..':
						xmlCV2.text = channel['cv2']

		xmlSong = ElementTree.ElementTree(xmlSong)
		xmlSong.write(filename) # I should make this auto-increment instead of accepting a filename!

	def setArtistEmailAddress(self, artistEmailAddress):
		self.artistEmailAddress = artistEmailAddress

	def setArtistName(self, artistName):
		self.artistName = artistName

	def setCV1(self, cv1):
		self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['cv1'] = cv1

	def setCV2(self, cv2):
		self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['cv2'] = cv2

	def setGate(self, gate):
		self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['gate'] = gate

	def setLoop(self, loop):
		self.loop = loop

	def setNumberOfChannels(self, numberOfChannels):
		self.cv1InCents = []
		self.cv1InCentsAndDots = []
		self.cv1InUnipolarVolts = []
		self.cv2InCents = []
		self.cv2InCentsAndDots = []
		self.cv2InUnipolarVolts = []
		self.gateInCents = []
		self.gateInCentsAndDots = []
		self.gateInUnipolarVolts = []
		self.pitchInChars = []
		self.pitchInCharsAndDots = []
		self.pitchInUnipolarVolts = []

		for channel in range(numberOfChannels):
			self.cv1InCents.append('00')
			self.cv1InCentsAndDots.append('..')
			self.cv1InUnipolarVolts.append(0.0)
			self.cv2InCents.append('00')
			self.cv2InCentsAndDots.append('..')
			self.cv2InUnipolarVolts.append(0.0)
			self.gateInCents.append('00')
			self.gateInCentsAndDots.append('..')
			self.gateInUnipolarVolts.append(0.0)
			self.pitchInChars.append('C-2')
			self.pitchInCharsAndDots.append('...')
			self.pitchInUnipolarVolts.append(0.0)

		self.numberOfChannels = numberOfChannels
		return True

	def setOctave(self, octave):
		semitone = self.getSemitone()

		if semitone == '..':
			semitone = 'C-'

		self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['pitch'] = semitone + str(octave)

	def setPitch(self, pitchInCharsAndDots):
		self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['pitch'] = pitchInCharsAndDots

	def setPlaying(self, playing):
		self.playing = playing

		if playing == True:
			self.patternPositionInSeconds = 0.0

	def setSemitone(self, semitone):
		octave = self.getOctave()

		if octave == '.':
			octave = 2 # An appropriately acidic default octave.  Neither "octave down" nor "octave up" are selected, if we have an acidic LED-based interface.

		self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['pitch'] = semitone + str(octave)

	def setSlide(self, slide):
		self.patternsInCentsAndDots[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['slide'] = slide

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
		self.averageRowLengthInSeconds = semiquaverLengthInSeconds

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
			self.cvInUnipolarVolts = self.cvInUnipolarVolts - (incrementLengthInSeconds / self.speedInUnipolarVolts)

	def setGate(self, gateInUnipolarVolts):
			self.gateInUnipolarVolts = gateInUnipolarVolts

			if gateInUnipolarVolts == 5:
				self.cvInUnipolarVolts = gateInUnipolarVolts

	def setSpeed(self, speedInUnipolarVolts):
		self.speedInUnipolarVolts = speedInUnipolarVolts
