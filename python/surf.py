# Stepper 1 library, for Python 3.

from xml.etree import ElementTree
from math import ceil, floor, pi, sin
from random import uniform
from struct import pack
import wave

globalIncrementLengthInSeconds = 1.0 / 44100.0

# Pseudo-constants:

try:
	DEFAULT_NUMBER_OF_ROWS
except NameError:
	DEFAULT_NUMBER_OF_ROWS = 64

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

class Sequencer:
	averageRowLengthInSeconds = 0.0
	clipboard = []
	clipboardFull = False
	currentChannelNumber = 0
	currentPatternNumber = 0
	currentRowNumber = 0
	cv1InTwelveBits = []
	cv1InUnipolarVolts = []
	cv2InTwelveBits = []
	cv2InUnipolarVolts = []
	finalPatternNumber = 0 # Final in the context of looping / playing
	gateInTwelveBits = []
	gateInUnipolarVolts = []
	nextPatternNumber = 0
	numberOfRows = 0
	patternPositionInSeconds = 0.0
	patternInSixtieths = []
	pitchInTwelveBits = []
	pitchInUnipolarVolts = []
	playMode = 0
	slideCV1 = True
	slideCV2 = True
	slidePitch = True
	swingInBipolarVolts = 0.0
	tempo = 120
	timeInSeconds = 0.0

	def __init__(self):
		for channel in range(NUMBER_OF_CHANNELS):
			self.cv1InTwelveBits.append(0)
			self.cv1InUnipolarVolts.append(0.0)
			self.cv2InTwelveBits.append(0)
			self.cv2InUnipolarVolts.append(0.0)
			self.gateInTwelveBits.append(0)
			self.gateInUnipolarVolts.append(0.0)
			self.pitchInTwelveBits.append(0)
			self.pitchInUnipolarVolts.append(0.0)

		self.setTempo(120) # Default to 120BPM
		self.reset()

	def addRow(self):
		if self.numberOfRows < MAX_NUMBER_OF_ROWS:
			self.numberOfRows = self.numberOfRows + 1

	def convertNumberIntoChars(self, number):
		"""Convert a number into three characters, suitable for display on an LCD."""
		number = int(number)
		number = '%03d' % number
		return number

	def convertPitchInSixtiethsIntoChars(self, sixtieth):
		"""Convert a number between 0 and 60 into three characters depicting the note in a more human readable form, suitable for display on a screen with a fixed width font."""
		semitone = sixtieth % 12
		octave = floor(sixtieth / 12.0)

		semitoneNames = ['C-', 'C#', 'D-', 'D#', 'E-', 'F-', 'F#', 'G-', 'G#', 'A-', 'A#', 'B-']

		semitone = semitoneNames[semitone]
		return semitone + str(octave)

	def convertSixtiethIntoChars(self, sixtieth):
		"""Convert a number between 0 and 60 into two characters, suitable for display on a screen with a fixed width font."""
		sixtieth = int(sixtieth) # This should be unnecessary.  It may be a sign that things need to be debugged.
		sixtieth = '%02d' % sixtieth
		return sixtieth

	def convertTwelveBitsIntoChars(self, twelveBits):
		"""Convert a number between 0 and 4095 into four characters, suitable for display on a screen with a fixed width font."""
		return '%04d' % twelveBits

	def copyPattern(self):
		self.clipboard = self.patternInSixtieths
		self.clipboardFull = True

	def decrementCurrentChannelNumber(self):
		if self.currentChannelNumber > 0:
			self.currentChannelNumber = self.currentChannelNumber - 1

	def decrementCurrentPatternNumber(self):
		if self.currentPatternNumber > 0:
			self.currentPatternNumber = self.currentPatternNumber - 1

	def decrementCurrentRowNumber(self):
		if self.currentRowNumber > 0:
			self.currentRowNumber = self.currentRowNumber - 1

	def decrementNextPatternNumber(self):
		if self.nextPatternNumber > 0:
			self.nextPatternNumber = self.currentPatternNumber - 1

	def decrementTempo(self):
		if self.tempo > 1:
			self.setTempo(self.tempo - 1)

	def getClipboardStatus(self):
		return self.clipboardFull

	def getCurrentChannelNumber(self):
		return self.currentChannelNumber

	def getCurrentPatternNumber(self):
		return self.currentPatternNumber

	def getCurrentRowNumber(self):
		return self.currentRowNumber

	def getCV1InSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['cv1']

	def getCV1InTwelveBits(self, channel):
		return self.cv1InTwelveBits[channel]

	def getCV1InUnipolarVolts(self, channel):
		return self.cv1InUnipolarVolts[channel]

	def getCV2InSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['cv2']

	def getCV2InTwelveBits(self, channel):
		return self.cv2InTwelveBits[channel]

	def getCV2InUnipolarVolts(self, channel):
		return self.cv2InUnipolarVolts[channel]

	def getGateInSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['gate']

	def getGateInTwelveBits(self, channel):
		return self.gateInTwelveBits[channel]

	def getGateInUnipolarVolts(self, channel):
		return self.gateInUnipolarVolts[channel]

	def getOctave(self):
		return floor(float(self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch']) / 12.0)

	def getPatternLength(self):
		return self.numberOfRows

	def getPitchInTwelveBits(self, channel):
		return self.pitchInTwelveBits[channel]

	def getPitchInUnipolarVolts(self, channel):
		return self.pitchInUnipolarVolts[channel]

	def getPitchInSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch']

	def getPlayMode(self):
		return self.playMode

	def getSemitone(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch'] % 12

	def getSlideInSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['slide']

	def getSwing(self):
		return self.swingInBipolarVolts

	def getTempo(self):
		return self.tempo

	def getTime(self):
		return self.timeInSeconds

	def getTrackLength(self):
		pass # This will involve loading in the pattern lengths from the file.

	def incrementCurrentChannelNumber(self):
		if self.currentChannelNumber < NUMBER_OF_CHANNELS - 1:
			self.currentChannelNumber = self.currentChannelNumber + 1

	def incrementCurrentPatternNumber(self):
		if self.currentPatternNumber < MAX_NUMBER_OF_PATTERNS - 1: # Count starting 0
			self.currentPatternNumber = self.currentPatternNumber + 1

	def incrementCurrentRowNumber(self):
		if self.currentRowNumber < self.numberOfRows - 1:
			self.currentRowNumber = self.currentRowNumber + 1

	def incrementNextPatternNumber(self):
		if self.nextPatternNumber != MAX_NUMBER_OF_PATTERNS - 1: # Count starting 0
			self.nextPatternNumber = self.nextPatternNumber + 1

	def incrementTempo(self):
		if self.tempo < 255:
			self.setTempo(self.tempo + 1)

	def incrementTime(self, incrementLengthInSeconds):
		if self.playMode == 0:
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

		if currentRowNumber > self.numberOfRows - 1:
			self.patternPositionInSeconds = 0.0
			# Do NOT increment self.timeInSeconds, that's the absolute time the sequencer's been running!

			# It doesn't look like we can continue on to the next iteration of the loop, so let's just reset everything to 0 instead, which is what would happen anyway.
			currentRowNumber = 0
			rowPairNumber = 0
			rowPairPositionInSeconds = 0.0
			rowPositionInSeconds = 0.0

			if self.playMode == 1:
				self.currentPatternNumber = self.nextPatternNumber
				self.loadPattern('memory.stepper1')
			elif self.playMode == 2:
				self.currentPatternNumber = self.currentPatternNumber + 1

				if self.currentPatternNumber > self.finalPatternNumber:
					self.currentPatternNumber = 0

				self.loadPattern('memory.stepper1')
			elif self.playMode == 3:
				self.currentPatternNumber = self.currentPatternNumber + 1

				if self.currentPatternNumber > self.finalPatternNumber:
					self.currentPatternNumber = 0
					self.playMode = 0

				self.loadPattern('memory.stepper1')

		self.currentRowNumber = currentRowNumber

		# Read in the current and next event rows
		nextRowNumber = currentRowNumber + 1

		if nextRowNumber > self.numberOfRows - 1:
			nextRowNumber = 0 # Wrap around from the last note in the pattern to the first note in the pattern.  Slide to that.  Let's not worry for now about whether the selected pattern will change.

		# Work out each current event's pitch, slide or lack thereof, gate length, CV1 and CV2
		for channel in range(NUMBER_OF_CHANNELS):
			# Convert the pitch to a control voltage, 1v/oct
			pitchInSixtieths = self.patternInSixtieths[self.currentRowNumber][channel]['pitch']
			self.pitchInTwelveBits[channel] = int(float(pitchInSixtieths) * 68.25) # / 60.0 * 4095.0
			self.pitchInUnipolarVolts[channel] = float(pitchInSixtieths) / 12.0 # / 60.0 * 5.0

			# Slide if necessary
			slide = self.patternInSixtieths[self.currentRowNumber][channel]['slide']

			# Set the gate length
			gateInSixtieths = self.patternInSixtieths[self.currentRowNumber][channel]['gate']
			gateLengthInSeconds = float(gateInSixtieths) / 60.0 * float(rowLengthInSeconds)

			# We need to make sure that we don't get any stray gate ons or gate offs, even for one single iteration
			if rowPositionInSeconds > gateLengthInSeconds or (rowPositionInSeconds == gateLengthInSeconds and gateLengthInSeconds == 0):
				self.gateInTwelveBits[channel] = 0
				self.gateInUnipolarVolts[channel] = 0.0
			else:
				self.gateInTwelveBits[channel] = 4095
				self.gateInUnipolarVolts[channel] = 5.0

			# Set CV1
			cv1InSixtieths = self.patternInSixtieths[self.currentRowNumber][channel]['cv1']
			self.cv1InTwelveBits[channel] = int(float(cv1InSixtieths) * 68.25) # / 60.0 * 4095.0
			self.cv1InUnipolarVolts[channel] = float(cv1InSixtieths) / 12.0 # / 60.0 * 5.0

			# Set CV2
			cv2InSixtieths = self.patternInSixtieths[self.currentRowNumber][channel]['cv2']
			self.cv2InTwelveBits[channel] = int(float(cv2InSixtieths) * 68.25) # / 60.0 * 4095.0
			self.cv2InUnipolarVolts[channel] = float(cv2InSixtieths) / 12.0 # / 60.0 * 5.0

			# Do the actual sliding
			if slide == 60:
				nextPitchInSixtieths = self.patternInSixtieths[nextRowNumber][channel]['pitch']
				nextPitchInTwelveBits = int(float(nextPitchInSixtieths) * 68.25) # / 60.0 * 4095.0
				nextPitchInUnipolarVolts = float(nextPitchInSixtieths) / 12.0 # / 60.0 * 5.0

				nextCV1InSixtieths = self.patternInSixtieths[nextRowNumber][channel]['cv1']
				nextCV1InTwelveBits = int(float(nextCV1InSixtieths) * 68.25) # / 60.0 * 4095.0
				nextCV1InUnipolarVolts = float(nextCV1InSixtieths) / 12.0 # / 60.0 * 5.0

				nextCV2InSixtieths = self.patternInSixtieths[nextRowNumber][channel]['cv2']
				nextCV2InTwelveBits = int(float(nextCV2InSixtieths) * 68.25) # / 60.0 * 4095.0
				nextCV2InUnipolarVolts = float(nextCV2InSixtieths) / 12.0 # / 60.0 * 5.0

				# Glide effortlessly and gracefully from the current event to the next
				if rowPositionInSeconds > rowLengthInSeconds / 2:
					pitchDifferenceInTwelveBits = nextPitchInTwelveBits - self.pitchInTwelveBits[channel]
					cv1DifferenceInTwelveBits = nextCV1InTwelveBits - self.cv1InTwelveBits[channel]
					cv2DifferenceInTwelveBits = nextCV2InTwelveBits - self.cv2InTwelveBits[channel]

					pitchDifferenceInUnipolarVolts = nextPitchInUnipolarVolts - self.pitchInUnipolarVolts[channel]
					cv1DifferenceInUnipolarVolts = nextCV1InUnipolarVolts - self.cv1InUnipolarVolts[channel]
					cv2DifferenceInUnipolarVolts = nextCV2InUnipolarVolts - self.cv2InUnipolarVolts[channel]

					# Work out how far along the slide we are, from 0 to 1
					beginningInSeconds = rowLengthInSeconds / 2
					endInSeconds = rowLengthInSeconds
					positionInSeconds = rowPositionInSeconds
					offsetPositionInSeconds = positionInSeconds - beginningInSeconds
					offsetEndInSeconds = endInSeconds - beginningInSeconds
					positionAsDecimal = offsetPositionInSeconds / offsetEndInSeconds

					if self.slidePitch == True:
						self.pitchInTwelveBits[channel] = int(self.pitchInTwelveBits[channel] + (pitchDifferenceInTwelveBits / 1 * positionAsDecimal))
						self.pitchInUnipolarVolts[channel] = self.pitchInUnipolarVolts[channel] + (pitchDifferenceInUnipolarVolts / 1 * positionAsDecimal)

					if self.slideCV1 == True:
						self.cv1InTwelveBits[channel] = int(self.cv1InTwelveBits[channel] + (cv1DifferenceInTwelveBits / 1 * positionAsDecimal))
						self.cv1InUnipolarVolts[channel] = self.cv1InUnipolarVolts[channel] + (cv1DifferenceInUnipolarVolts / 1 * positionAsDecimal)

					if self.slideCV2 == True:
						self.cv2InTwelveBits[channel] = int(self.cv2InTwelveBits[channel] + (cv2DifferenceInTwelveBits / 1 * positionAsDecimal))
						self.cv2InUnipolarVolts[channel] = self.cv2InUnipolarVolts[channel] + (cv2DifferenceInUnipolarVolts / 1 * positionAsDecimal)

		return incrementLengthInSeconds

	def loadPattern(self, filename):
		# Wipe the old pattern
		self.reset()

		# Load the new song
		song = open(filename, 'r')

		# Load the pattern length
		song.seek(self.currentPatternNumber)
		self.numberOfRows = ord(song.read(1))

		# Seek ahead
		song.seek(MAX_NUMBER_OF_PATTERNS + (self.currentPatternNumber * MAX_NUMBER_OF_ROWS * NUMBER_OF_CHANNELS * 5)) # 5 bytes per event

		# Load the current pattern
		for currentRowNumber in range(MAX_NUMBER_OF_ROWS):
			for currentChannelNumber in range(NUMBER_OF_CHANNELS):
				firstByte = song.read(1)

				if not firstByte: # End of file.  Nothing to load.  This pattern doesn't exist yet.
					return

				pitch = ord(firstByte)
				slide = ord(song.read(1))
				gate = ord(song.read(1))
				cv1 = ord(song.read(1))
				cv2 = ord(song.read(1))

				self.patternInSixtieths[currentRowNumber][currentChannelNumber]['pitch'] = pitch
				self.patternInSixtieths[currentRowNumber][currentChannelNumber]['slide'] = slide
				self.patternInSixtieths[currentRowNumber][currentChannelNumber]['gate'] = gate
				self.patternInSixtieths[currentRowNumber][currentChannelNumber]['cv1'] = cv1
				self.patternInSixtieths[currentRowNumber][currentChannelNumber]['cv2'] = cv2

		currentRowNumber = currentRowNumber + 1
		song.close()

	def pastePattern(self):
		self.patternInSixtieths = self.clipboard
		self.clipboard = []
		self.clipboardFull = False

	def removeRow(self):
		if self.numberOfRows > 1:
			self.numberOfRows = self.numberOfRows - 1

			for channel in range(NUMBER_OF_CHANNELS):
				self.patternInSixtieths[self.numberOfRows][channel] = {'pitch': 24, 'slide': 0, 'gate': 0, 'cv1': 0, 'cv2': 0} # Reset removed row to defaults, namely silent Cs.  We would add 1 to the number of rows, as we want to go one above it, but remember that us hackers count starting with 0.

	def reset(self):
		"""Clear the pattern held in memory."""
		self.numberOfRows = DEFAULT_NUMBER_OF_ROWS
		self.patternInSixtieths = []

		for row in range(MAX_NUMBER_OF_ROWS):
			self.patternInSixtieths.append([])

			for channel in range(NUMBER_OF_CHANNELS):
				self.patternInSixtieths[row].append([])
				self.patternInSixtieths[row][channel] = {'pitch': 24, 'slide': 0, 'gate': 0, 'cv1': 0, 'cv2': 0} # Reset removed row to defaults, namely silent Cs

	def savePattern(self, filename):
		# Save the current song
		try:
			song = open(filename, 'r+') # If it already exists, open the file in read/write mode so seeking past some data won't blat those data.
		except IOError:
			song = open(filename, 'w') # If it doesn't already exist, create it first.

			# Write a whole file of defaults first
			for pattern in range(MAX_NUMBER_OF_PATTERNS):
				song.write(chr(DEFAULT_NUMBER_OF_ROWS))

			for event in range(MAX_NUMBER_OF_PATTERNS * MAX_NUMBER_OF_ROWS * NUMBER_OF_CHANNELS):
				song.write(chr(24) + chr(0) + chr(0) + chr(0) + chr(0))

			song.close()

			# Now re-open the file as normal
			song = open(filename, 'r+') # Now we know it already exists, open the file again, this time in read/write mode so seeking past some data won't blat those data.

		# Save the pattern length
		song.seek(self.currentPatternNumber)
		numberOfRows = chr(self.numberOfRows)
		song.write(numberOfRows)

		# Seek ahead
		song.seek(MAX_NUMBER_OF_PATTERNS + (self.currentPatternNumber * MAX_NUMBER_OF_ROWS * NUMBER_OF_CHANNELS * 5)) # 5 bytes per event

		# Save the current pattern
		for currentRowNumber in range(MAX_NUMBER_OF_ROWS):
			for currentChannelNumber in range(NUMBER_OF_CHANNELS):
				pitch = chr(self.patternInSixtieths[currentRowNumber][currentChannelNumber]['pitch'])
				slide = chr(self.patternInSixtieths[currentRowNumber][currentChannelNumber]['slide'])
				gate = chr(self.patternInSixtieths[currentRowNumber][currentChannelNumber]['gate'])
				cv1 = chr(self.patternInSixtieths[currentRowNumber][currentChannelNumber]['cv1'])
				cv2 = chr(self.patternInSixtieths[currentRowNumber][currentChannelNumber]['cv2'])
				song.write(pitch + slide + gate + cv1 + cv2)

		song.close()

	def setCV1(self, cv1):
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['cv1'] = cv1

	def setCV2(self, cv2):
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['cv2'] = cv2

	def setGate(self, gate):
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['gate'] = gate

	def setOctave(self, octave):
		semitone = self.getSemitone()
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch'] = semitone + (octave * 12)

	def setPitch(self, pitchInSixtieths):
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch'] = pitchInSixtieths

	def setPlayMode(self, playMode):
		self.playMode = playMode

		# Technically, nextPatternNumber and finalPatternNumber could probably be the same variable, but I wouldn't advise that as it would be needlessly confusing.
		if playMode == 0:
			pass
		elif playMode == 1:
			self.patternPositionInSeconds = 0.0
			self.nextPatternNumber = self.currentPatternNumber # Play mode 1 will use this default, unless the user queues up a pattern change in the meantime.
		else:
			self.patternPositionInSeconds = 0.0
			self.finalPatternNumber = self.currentPatternNumber # Play modes 2 and 3 will use this.
			self.currentPatternNumber = 0

	def setSemitone(self, semitone):
		octave = self.getOctave()
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch'] = semitone + (octave * 12)

	def setSlide(self, slide):
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['slide'] = slide

	def setSwing(self, swingInBipolarVolts):
		self.swingInBipolarVolts = swingInBipolarVolts

	def setTempo(self, tempo):
		self.tempo = int(tempo)
		crotchetLengthInSeconds = 60.0 / float(self.tempo)
		semiquaverLengthInSeconds = crotchetLengthInSeconds / 4.0
		self.averageRowLengthInSeconds = semiquaverLengthInSeconds

	def transposePatternDown(self):
		# Only transpose down if every note in the pattern will still be in the 0 to 60 range afterwards
		lowestPitch = 60

		for row in self.patternInSixtieths:
			for channel in row:
				if channel['pitch'] < lowestPitch:
					lowestPitch = channel['pitch']

		if lowestPitch == 0:
			return

		# Go ahead and transpose the pattern
		for row in self.patternInSixtieths:
			for channel in row:
					channel['pitch'] = channel['pitch'] - 1

	def transposePatternUp(self):
		# Only transpose up if every note in the pattern will still be in the 0 to 60 range afterwards
		highestPitch = 0

		for row in self.patternInSixtieths:
			for channel in row:
				if channel['pitch'] > highestPitch:
					highestPitch = channel['pitch']

		if highestPitch == 60:
			return

		# Go ahead and transpose the pattern
		for row in self.patternInSixtieths:
			for channel in row:
					channel['pitch'] = channel['pitch'] + 1
