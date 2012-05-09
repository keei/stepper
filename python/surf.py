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
import wave

globalIncrementLengthInSeconds = 1.0 / 44100.0

# Pseudo-constants:

try:
	MAX_NUMBER_OF_PATTERNS
except NameError:
	MAX_NUMBER_OF_PATTERNS = 64

try:
	MAX_NUMBER_OF_ROWS
except NameError:
	MAX_NUMBER_OF_ROWS = 64

try:
	NUMBER_OF_CHANNELS
except NameError:
	NUMBER_OF_CHANNELS = 4

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
		self.outputFile = wave.open(self.filename, 'w')
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
	averageRowLengthInSeconds = 0.0
	clipboard = []
	clipboardFull = False
	currentChannelNumber = 0
	currentRowNumber = 0
	currentPatternNumber = 0
	cv1InSixtieths = []
	cv1InUnipolarVolts = []
	cv2InSixtieths = []
	cv2InUnipolarVolts = []
	gateInSixtieths = []
	gateInUnipolarVolts = []
	loop = False
	# noteCvLookupTable = [0.0, 0.083, 0.166, 0.25, 0.333, 0.416, 0.5, 0.583, 0.666, 0.75, 0.833, 0.916] # I should use this
	numberOfPatterns = 1
	numberOfRows = []
	patternPositionInSeconds = 0.0
	patternsInSixtieths = []
	pitchInSixtieths = []
	pitchInUnipolarVolts = []
	playing = False
	swingInBipolarVolts = 0.0
	tempo = 120
	timeInSeconds = 0.0

	def __init__(self):
		for channel in range(NUMBER_OF_CHANNELS):
			self.cv1InSixtieths.append(0)
			self.cv1InUnipolarVolts.append(0.0)
			self.cv2InSixtieths.append(0)
			self.cv2InUnipolarVolts.append(0.0)
			self.gateInSixtieths.append(0)
			self.gateInUnipolarVolts.append(0.0)
			self.pitchInSixtieths.append(12)
			self.pitchInUnipolarVolts.append(0.0)

		self.reset()

	def addPattern(self):
		if self.numberOfPatterns < MAX_NUMBER_OF_PATTERNS:
			self.numberOfPatterns = self.numberOfPatterns + 1

	def addRow(self):
		if self.numberOfRows[self.currentPatternNumber] < MAX_NUMBER_OF_ROWS:
			self.numberOfRows[self.currentPatternNumber] = self.numberOfRows[self.currentPatternNumber] + 1

	def convertNumberIntoChars(self, number):
		"""Convert a number into three characters, suitable for display on an LCD."""
		number = int(number)
		number = '%03d' % number
		return number

	def convertSixtiethIntoChars(self, sixtieth):
		"""Convert a number between 0 and 60 into two characters, suitable for display on a screen with a fixed width font."""
		sixtieth = int(sixtieth) # This should be unnecessary.  It may be a sign that things need to be debugged.
		sixtieth = '%02d' % sixtieth

		return sixtieth

	def copyPattern(self):
		self.clipboard = self.patternsInSixtieths[self.currentPatternNumber]
		self.clipboardFull = True

	def decrementCurrentChannelNumber(self):
		if self.currentChannelNumber > 0:
			self.currentChannelNumber = self.currentChannelNumber - 1

	def decrementCurrentRowNumber(self):
		if self.currentRowNumber > 0:
			self.currentRowNumber = self.currentRowNumber - 1

	def decrementCurrentPatternNumber(self):
		if self.currentPatternNumber > 0:
			self.currentPatternNumber = self.currentPatternNumber - 1

	def decrementTempo(self):
		if self.tempo > 1:
			self.setTempo(self.tempo - 1)

	def getArtistEmailAddress(self, artistEmailAddress):
		return self.artistEmailAddress

	def getArtistName(self, artistName):
		return self.artistName

	def getClipboardStatus(self):
		return self.clipboardFull

	def getCurrentChannelNumber(self):
		return self.currentChannelNumber

	def getCurrentRowNumber(self):
		return self.currentRowNumber

	def getCurrentPatternNumber(self):
		return self.currentPatternNumber

	def getCV1InSixtieths(self):
		return self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['cv1']

	def getCV1Output(self, channel):
		return self.cv1InUnipolarVolts[channel]

	def getCV2InSixtieths(self):
		return self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['cv2']

	def getCV2Output(self, channel):
		return self.cv2InUnipolarVolts[channel]

	def getGateInSixtieths(self):
		return self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['gate']

	def getGateOutput(self, channel):
		return self.gateInUnipolarVolts[channel]

	def getLoopTime(self):
		return self.patternPositionInSeconds

	def getOctave(self):
		return floor(float(self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['pitch']) / 12.0)

	def getPatternLength(self):
		return self.numberOfRows[self.currentPatternNumber]

	def getPitchOutput(self, channel):
		return self.pitchInUnipolarVolts[channel]

	def getPitchInSixtieths(self):
		return self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['pitch']

	def getPlaying(self):
		return self.playing

	def getSemitone(self):
		return self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['pitch'] % 12

	def getSlideInSixtieths(self):
		return self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['slide']

	def getSongInformation(self, songInformation):
		return self.songInformation

	def getSongName(self, songName):
		return self.songName

	def getSwing(self):
		return self.swingInBipolarVolts

	def getTempo(self):
		return self.tempo

	def getTime(self):
		return self.timeInSeconds

	def getTrackLength(self):
		return sum(self.numberOfRows) * self.averageRowLengthInSeconds # This is now grossly oversimplifying!

	def incrementCurrentChannelNumber(self):
		if self.currentChannelNumber < NUMBER_OF_CHANNELS - 1:
			self.currentChannelNumber = self.currentChannelNumber + 1

	def incrementCurrentRowNumber(self):
		if self.currentRowNumber < self.numberOfRows[self.currentPatternNumber]:
			self.currentRowNumber = self.currentRowNumber + 1

	def incrementCurrentPatternNumber(self):
		if self.currentPatternNumber == MAX_NUMBER_OF_PATTERNS - 1: # Count starting 0
			return

		if self.currentPatternNumber == self.numberOfPatterns - 1:
			self.numberOfPatterns = self.numberOfPatterns + 1

		self.currentPatternNumber = self.currentPatternNumber + 1

	def incrementTempo(self):
		if self.tempo < 300:
			self.setTempo(self.tempo + 1)

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

		if currentRowNumber > self.numberOfRows[self.currentPatternNumber] - 1:
			if self.loop == True:
				self.patternPositionInSeconds = 0.0
				# Do NOT increment self.timeInSeconds, that's the absolute time the sequencer's been running!

				# It doesn't look like we can continue on to the next iteration of the loop, so let's just reset everything to 0 instead, which is what would happen anyway.
				currentRowNumber = 0
				rowPairNumber = 0
				rowPairPositionInSeconds = 0.0
				rowPositionInSeconds = 0.0
			else:
				currentRowNumber = len(self.patternsInSixtieths[self.currentPatternNumber]) - 1

		self.currentRowNumber = currentRowNumber

		# Read in the current and next event rows
		nextRowNumber = currentRowNumber + 1

		if nextRowNumber > len(self.patternsInSixtieths[self.currentPatternNumber]) - 1:
			nextRowNumber = 0 # Wrap around from the last note in the pattern to the first note in the pattern.  Slide to that.  Let's not worry for now about whether the selected pattern will change.

		# Work out each current event's pitch, slide or lack thereof, gate length, CV1 and CV2
		for channel in range(NUMBER_OF_CHANNELS):
			# Convert the pitch to a control voltage, 1v/oct
			pitchInSixtieths = self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][channel]['pitch']
			self.pitchInUnipolarVolts[channel] = float(pitchInSixtieths) * 0.083 # I should improve this

			# Slide if necessary
			slide = self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][channel]['slide']

			# Set the gate length
			gateInSixtieths = self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][channel]['gate']
			gateLengthInSeconds = float(gateInSixtieths) / 60.0 * float(rowLengthInSeconds)

			# We need to make sure that we don't get any stray gate ons or gate offs, even for one single iteration
			if rowPositionInSeconds > gateLengthInSeconds or (rowPositionInSeconds == gateLengthInSeconds and gateLengthInSeconds == 0):
				self.gateInUnipolarVolts[channel] = 0.0
			else:
				self.gateInUnipolarVolts[channel] = 5.0

			# Set CV1
			cv1InSixtieths = self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][channel]['cv1']
			self.cv1InUnipolarVolts[channel] = float(cv1InSixtieths) / 12.0 # / 60.0 * 5.0

			# Set CV2
			cv2InSixtieths = self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][channel]['cv2']
			self.cv2InUnipolarVolts[channel] = float(cv2InSixtieths) / 12.0 # / 60.0 * 5.0

			# Do the actual sliding
			if slide == 60:
				nextPitchInSixtieths = self.patternsInSixtieths[self.currentPatternNumber][nextRowNumber][channel]['pitch']
				nextPitchInUnipolarVolts = float(nextPitchInSixtieths) * 0.08333 # I should improve this

				nextEventCV1 = self.patternsInSixtieths[self.currentPatternNumber][nextRowNumber][channel]['cv1']
				nextCV1InUnipolarVolts = float(nextEventCV1) / 12.0 # / 60.0 * 5.0

				nextEventCV2 = self.patternsInSixtieths[self.currentPatternNumber][nextRowNumber][channel]['cv2']
				nextCV2InUnipolarVolts = float(nextEventCV2) / 12.0 # / 60.0 * 5.0

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
		# Wipe the old song
		self.reset()

		# Load in the new song
		song = open(filename, 'r')

		for currentPatternNumber in range(MAX_NUMBER_OF_PATTERNS):
			for currentRowNumber in range(MAX_NUMBER_OF_ROWS):
				for currentChannelNumber in range(NUMBER_OF_CHANNELS):
					pitch = ord(song.read(1)) - 48
					slide = ord(song.read(1)) - 48
					gate = ord(song.read(1)) - 48
					cv1 = ord(song.read(1)) - 48
					cv2 = ord(song.read(1)) - 48

					self.patternsInSixtieths[currentPatternNumber][currentRowNumber][currentChannelNumber]['pitch'] = pitch
					self.patternsInSixtieths[currentPatternNumber][currentRowNumber][currentChannelNumber]['slide'] = slide
					self.patternsInSixtieths[currentPatternNumber][currentRowNumber][currentChannelNumber]['gate'] = gate
					self.patternsInSixtieths[currentPatternNumber][currentRowNumber][currentChannelNumber]['cv1'] = cv1
					self.patternsInSixtieths[currentPatternNumber][currentRowNumber][currentChannelNumber]['cv2'] = cv2

			currentRowNumber = currentRowNumber + 1

	def pastePattern(self):
		self.patternsInSixtieths[self.currentPatternNumber] = self.clipboard
		self.clipboard = []
		self.clipboardFull = False

	def removeRow(self):
		if self.numberOfRows[self.currentPatternNumber] > 1:
			self.numberOfRows[self.currentPatternNumber] = self.numberOfRows[self.currentPatternNumber] - 1

			for channel in range(NUMBER_OF_CHANNELS):
				self.patternsInSixtieths[self.currentPatternNumber][self.numberOfRows[self.currentPatternNumber]][channel] = {'pitch': 12, 'slide': 0, 'gate': 0, 'cv1': 0, 'cv2': 0} # Reset removed row to defaults, namely silent Cs.  We would add 1 to the number of rows, as we want to go one above it, but remember that us hackers count starting with 0.

	def reset(self):
		self.setTempo(120) # Default to 120BPM
		self.numberOfRows = []

		for pattern in range(MAX_NUMBER_OF_PATTERNS):
			self.numberOfRows.append(MAX_NUMBER_OF_ROWS)

		self.patternsInSixtieths = []

		for pattern in range(MAX_NUMBER_OF_PATTERNS):
			self.patternsInSixtieths.append([])

			for row in range(MAX_NUMBER_OF_ROWS):
				self.patternsInSixtieths[pattern].append([])

				for channel in range(NUMBER_OF_CHANNELS):
					self.patternsInSixtieths[pattern][row].append([])
					self.patternsInSixtieths[pattern][row][channel] = {'pitch': 12, 'slide': 0, 'gate': 0, 'cv1': 0, 'cv2': 0} # Reset removed row to defaults, namely silent Cs

	def saveSong(self, filename):
		# Save the current song
		song = open(filename, 'w')

		currentPatternNumber = 0
		# currentRowNumber = 0

		for pattern in self.patternsInSixtieths:
			currentPatternNumber = currentPatternNumber + 1

			for row in pattern:
				# currentRowNumber = currentRowNumber + 1

				for currentChannelNumber in range(NUMBER_OF_CHANNELS):
					# In C, we'd use self.patternsInSixtieths[currentPatternNumber][currentRowNumber][currentChannelNumber]['pitch'] etc.
					# I'm only adding 48 to everything to make the output happen to be printable ASCII.  As we're only using 61 numbers anyway, we might as well choose the pretty ones.
					pitch = chr(row[currentChannelNumber]['pitch'] + 48)
					slide = chr(row[currentChannelNumber]['slide'] + 48)
					gate = chr(row[currentChannelNumber]['gate'] + 48)
					cv1 = chr(row[currentChannelNumber]['cv1'] + 48)
					cv2 = chr(row[currentChannelNumber]['cv2'] + 48)
					song.write(pitch + slide + gate + cv1 + cv2)

	def setArtistEmailAddress(self, artistEmailAddress):
		self.artistEmailAddress = artistEmailAddress

	def setArtistName(self, artistName):
		self.artistName = artistName

	def setCV1(self, cv1):
		self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['cv1'] = cv1

	def setCV2(self, cv2):
		self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['cv2'] = cv2

	def setGate(self, gate):
		self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['gate'] = gate

	def setLoop(self, loop):
		self.loop = loop

	def setOctave(self, octave):
		semitone = self.getSemitone()
		self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['pitch'] = semitone + (octave * 12)

	def setPitch(self, pitchInSixtieths):
		self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['pitch'] = pitchInSixtieths

	def setPlaying(self, playing):
		self.playing = playing

		if playing == True:
			self.patternPositionInSeconds = 0.0

	def setSemitone(self, semitone):
		octave = self.getOctave()
		self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['pitch'] = semitone + (octave * 12)

	def setSlide(self, slide):
		self.patternsInSixtieths[self.currentPatternNumber][self.currentRowNumber][self.currentChannelNumber]['slide'] = slide

	def setSongInformation(self, songInformation):
		self.songInformation = songInformation

	def setSongName(self, songName):
		self.songName = songName

	def setSwing(self, swingInBipolarVolts):
		self.swingInBipolarVolts = swingInBipolarVolts

	def setTempo(self, tempo):
		self.tempo = int(tempo)
		crotchetLengthInSeconds = 60.0 / float(self.tempo)
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
