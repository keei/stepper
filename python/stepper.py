# Stepper 1 library, for Python 3.

# Pseudo-constants:

try:
	DEFAULT_NUMBER_OF_ROWS
except NameError:
	DEFAULT_NUMBER_OF_ROWS = 64

try:
	DEFAULT_PITCH
except NameError:
	DEFAULT_PITCH = 24 # C-2

try:
	DEFAULT_TEMPO
except NameError:
	DEFAULT_TEMPO = 120

try:
	FILENAME
except NameError:
	FILENAME = 'stepper.stp'

try:
	FROM_SIXTIETHS_TO_TWELVE_BITS
except NameError:
	FROM_SIXTIETHS_TO_TWELVE_BITS = 68.25 # Multiplying by 68.25 is the same as dividing by 60.0 and multiplying by 4095.0

try:
	HIGH
except NameError:
	HIGH = 4095

try:
	LOW
except NameError:
	LOW = 0

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

try:
	PULSES_PER_QUARTER_NOTE
except NameError:
	PULSES_PER_QUARTER_NOTE = 24 # 24PPQN for Roland compatability; 48PPQN for Korg compatability.

try:
	SEMITONES_IN_OCTAVE_FLOAT
except NameError:
	SEMITONES_IN_OCTAVE_FLOAT = 12.0

try:
	SEMITONES_IN_OCTAVE_INT
except NameError:
	SEMITONES_IN_OCTAVE_INT = 12

class Sequencer:
	absoluteLastDinSyncTriggerInputInMicroseconds = 0
	absoluteTimeInMicroseconds = 0
	averageRowLengthInMicroseconds = 0
	clipboard = []
	clipboardFull = False
	currentChannelNumber = 0
	currentPatternNumber = 0
	currentRowNumber = 0
	cv1InTwelveBits = []
	cv2InTwelveBits = []
	dinSyncGateInputInTwelveBits = LOW
	dinSyncGateOutputInTwelveBits = LOW
	dinSyncTriggerInputInTwelveBits = LOW
	dinSyncTriggerOutputInTwelveBits = LOW
	dinSyncTriggerOutputLengthInMicroseconds = 1000000
	finalPatternNumber = 0 # Final in the context of looping / playing
	gateInTwelveBits = []
	lastPlayMode = 1
	nextPatternNumber = 0
	numberOfRows = 0
	patternPositionInMicroseconds = 0
	patternInSixtieths = []
	pitchInTwelveBits = []
	playMode = 0
	playTimeInMicroseconds = 0
	queuedDinSyncGateOutput = LOW # What the DIN sync gate (run/stop) should be at the time of the next DIN sync trigger (clock pulse).  I'm guessing it needs to patiently wait until the next one, so let's do that.
	slideCV1 = True
	slideCV2 = True
	slidePitch = True
	swing = 0 # In the range of -127 to +127, in other words a signed char in C.
	tapeSyncOutputInTwelveBits = LOW
	tempo = DEFAULT_TEMPO # In the range of 1 to 255, in other words an unsigned char in C.
	triggerClipboard = []
	triggerInTwelveBits = []
	triggerPattern = []

	def __init__(self):
		for channel in range(NUMBER_OF_CHANNELS):
			self.cv1InTwelveBits.append(0)
			self.cv2InTwelveBits.append(0)
			self.gateInTwelveBits.append(LOW)
			self.pitchInTwelveBits.append(1638) # C-2

		for channel in range(8):
			self.triggerInTwelveBits.append(LOW)

		self.setTempo(DEFAULT_TEMPO)
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
		semitone = sixtieth % SEMITONES_IN_OCTAVE_INT
		octave = int(sixtieth / SEMITONES_IN_OCTAVE_FLOAT)

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

	def convertTriggerByteIntoChars(self, number):
		"""Convert a byte into eight characters, suitable for display on a screen with a fixed width font."""
		string = ''

		for i in range(8):
			if number & 1 << i: # "2 << i" basically means "Two to the power of i"
				string = 'o' + string
			else:
				string = '.' + string

		return string

	def copyPattern(self):
		self.clipboard = self.patternInSixtieths
		self.triggerClipboard = self.triggerPattern
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

	def getAbsoluteTime(self):
		return self.absoluteTimeInMicroseconds

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

	def getCV2InSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['cv2']

	def getCV2InTwelveBits(self, channel):
		return self.cv2InTwelveBits[channel]

	def getDinSyncGateOutputInTwelveBits(self):
		return self.dinSyncGateOutputInTwelveBits

	def getDinSyncTriggerOutputInTwelveBits(self):
		return self.dinSyncTriggerOutputInTwelveBits

	def getGateInSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['gate']

	def getGateInTwelveBits(self, channel):
		return self.gateInTwelveBits[channel]

	def getOctave(self):
		return int(float(self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch']) / SEMITONES_IN_OCTAVE_FLOAT)

	def getPatternLength(self):
		return self.numberOfRows

	def getPitchInTwelveBits(self, channel):
		return self.pitchInTwelveBits[channel]

	def getPitchInSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch']

	def getPlayMode(self):
		return self.playMode

	def getPlayTime(self):
		return self.playTimeInMicroseconds

	def getSemitone(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch'] % SEMITONES_IN_OCTAVE_INT

	def getSlideInSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['slide']

	def getSwing(self):
		return self.swing

	def getTapeSyncTriggerOutputInTwelveBits(self):
		return self.tapeSyncOutputInTwelveBits

	def getTempo(self):
		return self.tempo

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

	def incrementTime(self, incrementLengthInMicroseconds):
		# Send syncing information as appropriate, even if we're paused
		self.absoluteTimeInMicroseconds = self.absoluteTimeInMicroseconds + incrementLengthInMicroseconds

		# Send out a DIN sync trigger
		# The DIN sync trigger (clock pulse) has a duty cycle of 50%.  Let's use simple modulo arithmetic.
		if self.absoluteTimeInMicroseconds % self.dinSyncTriggerOutputLengthInMicroseconds < self.dinSyncTriggerOutputLengthInMicroseconds / 2:
			# If the DIN sync trigger's making the transition from low to high RIGHT NOW, then it's the first iteration of the loop during this clock cycle.  That's the only time we can change whether we're playing or paused, for bang on timing.
			if self.dinSyncTriggerOutputInTwelveBits == LOW:
				if self.queuedDinSyncGateOutput == HIGH:
					self.dinSyncGateOutputInTwelveBits = HIGH
				else:
					self.dinSyncGateOutputInTwelveBits = LOW

			self.dinSyncTriggerOutputInTwelveBits = HIGH

		else:
			self.dinSyncTriggerOutputInTwelveBits = LOW

		# The tape sync trigger's a faster pulse wave (1200Hz for low, 2400Hz for high) representing the DIN sync trigger
		if self.dinSyncGateOutputInTwelveBits == HIGH and self.dinSyncTriggerOutputInTwelveBits == HIGH: # Only send the tape sync high signal if the DIN sync clock pulse and DIN sync gate are both high, and the first DIN sync clock pulse has started since the DIN sync gate went high (the latter currently being designated in my code as dinSyncGateOutputInTwelveBits, as opposed to queuedDinSyncGateOutput)
			if self.absoluteTimeInMicroseconds % (5000 / 12) < 5000 / 24: # (1 second / 2400 Hz) * 1000000 microseconds in a second = 1000000 / 2400 = 5000 / 12 = 1000 / 2.4 etc.
				self.tapeSyncOutputInTwelveBits = HIGH
			else:
				self.tapeSyncOutputInTwelveBits = LOW
		else:
			if self.absoluteTimeInMicroseconds % (5000 / 6) < 5000 / 12: # (1 second / 1200 Hz) * 1000000 microseconds in a second = 1000000 / 1200 = 5000 / 6 = 1000 / 1.2 etc.
				self.tapeSyncOutputInTwelveBits = HIGH
			else:
				self.tapeSyncOutputInTwelveBits = LOW

		# Play the pattern only if we're playing
		if self.dinSyncGateOutputInTwelveBits == LOW:
			return

		self.playTimeInMicroseconds = self.playTimeInMicroseconds + incrementLengthInMicroseconds
		self.patternPositionInMicroseconds = self.patternPositionInMicroseconds + incrementLengthInMicroseconds
		rowPairLengthInMicroseconds = self.averageRowLengthInMicroseconds * 2

		# Work out the current event row
		rowPairNumber = int(self.patternPositionInMicroseconds // rowPairLengthInMicroseconds)
		currentRowNumber = rowPairNumber * 2

		swingAsDecimal = (self.swing + 127.0) / 254.0
		firstRowLengthInMicroseconds = self.averageRowLengthInMicroseconds / 0.5 * swingAsDecimal
		rowPairPositionInMicroseconds = self.patternPositionInMicroseconds - (rowPairLengthInMicroseconds * rowPairNumber)

		if rowPairPositionInMicroseconds > firstRowLengthInMicroseconds:
			currentRowNumber = currentRowNumber + 1
			rowLengthInMicroseconds = rowPairLengthInMicroseconds - firstRowLengthInMicroseconds
			rowPositionInMicroseconds = rowPairPositionInMicroseconds - firstRowLengthInMicroseconds
		else:
			rowLengthInMicroseconds = firstRowLengthInMicroseconds
			rowPositionInMicroseconds = rowPairPositionInMicroseconds

		if currentRowNumber > self.numberOfRows - 1:
			self.patternPositionInMicroseconds = 0

			# It doesn't look like we can continue on to the next iteration of the loop, so let's just reset everything to 0 instead, which is what would happen anyway.
			currentRowNumber = 0
			rowPairNumber = 0
			rowPairPositionInMicroseconds = 0
			rowPositionInMicroseconds = 0

			if self.playMode == 1:
				self.currentPatternNumber = self.nextPatternNumber
				self.loadPattern(FILENAME)
			elif self.playMode == 2:
				self.currentPatternNumber = self.currentPatternNumber + 1

				if self.currentPatternNumber > self.finalPatternNumber:
					self.currentPatternNumber = 0

				self.loadPattern(FILENAME)
			elif self.playMode == 3:
				self.currentPatternNumber = self.currentPatternNumber + 1

				if self.currentPatternNumber > self.finalPatternNumber:
					self.currentPatternNumber = 0
					self.playMode = 0
					self.queuedDinSyncGateOutput = LOW
					self.playTimeInMicroseconds = 0

				self.loadPattern(FILENAME)

		self.currentRowNumber = currentRowNumber

		# Read in the current and next event rows
		nextRowNumber = currentRowNumber + 1

		if nextRowNumber > self.numberOfRows - 1:
			nextRowNumber = 0 # Wrap around from the last note in the pattern to the first note in the pattern.  Slide to that.  Let's not worry for now about whether the selected pattern will change.

		# Work out each current event's pitch, slide or lack thereof, gate length, CV1 and CV2
		for channel in range(NUMBER_OF_CHANNELS):
			# Convert the pitch to a control voltage, 1v/oct
			pitchInSixtieths = self.patternInSixtieths[self.currentRowNumber][channel]['pitch']
			self.pitchInTwelveBits[channel] = int(float(pitchInSixtieths) * FROM_SIXTIETHS_TO_TWELVE_BITS)

			# Slide if necessary
			slide = self.patternInSixtieths[self.currentRowNumber][channel]['slide']

			# Set the gate length
			gateInSixtieths = self.patternInSixtieths[self.currentRowNumber][channel]['gate']
			gateLengthInMicroseconds = int(float(gateInSixtieths) / 60.0 * float(rowLengthInMicroseconds))

			# We need to make sure that we don't get any stray gate ons or gate offs, even for one single iteration
			if rowPositionInMicroseconds > gateLengthInMicroseconds or (rowPositionInMicroseconds == gateLengthInMicroseconds and gateLengthInMicroseconds == 0):
				self.gateInTwelveBits[channel] = LOW
			else:
				self.gateInTwelveBits[channel] = HIGH

			# Set CV1
			cv1InSixtieths = self.patternInSixtieths[self.currentRowNumber][channel]['cv1']
			self.cv1InTwelveBits[channel] = int(float(cv1InSixtieths) * FROM_SIXTIETHS_TO_TWELVE_BITS)

			# Set CV2
			cv2InSixtieths = self.patternInSixtieths[self.currentRowNumber][channel]['cv2']
			self.cv2InTwelveBits[channel] = int(float(cv2InSixtieths) * FROM_SIXTIETHS_TO_TWELVE_BITS)

			# Do the actual sliding
			if slide == 60:
				nextPitchInSixtieths = self.patternInSixtieths[nextRowNumber][channel]['pitch']
				nextPitchInTwelveBits = int(float(nextPitchInSixtieths) * FROM_SIXTIETHS_TO_TWELVE_BITS)

				nextCV1InSixtieths = self.patternInSixtieths[nextRowNumber][channel]['cv1']
				nextCV1InTwelveBits = int(float(nextCV1InSixtieths) * FROM_SIXTIETHS_TO_TWELVE_BITS)

				nextCV2InSixtieths = self.patternInSixtieths[nextRowNumber][channel]['cv2']
				nextCV2InTwelveBits = int(float(nextCV2InSixtieths) * FROM_SIXTIETHS_TO_TWELVE_BITS)

				# Glide effortlessly and gracefully from the current event to the next
				if rowPositionInMicroseconds > rowLengthInMicroseconds / 2:
					pitchDifferenceInTwelveBits = nextPitchInTwelveBits - self.pitchInTwelveBits[channel]
					cv1DifferenceInTwelveBits = nextCV1InTwelveBits - self.cv1InTwelveBits[channel]
					cv2DifferenceInTwelveBits = nextCV2InTwelveBits - self.cv2InTwelveBits[channel]

					# Work out how far along the slide we are, from 0 to 1
					beginningInMicroseconds = rowLengthInMicroseconds / 2
					positionAsDecimal = (rowPositionInMicroseconds - beginningInMicroseconds) / (rowLengthInMicroseconds - beginningInMicroseconds)

					if self.slidePitch == True:
						self.pitchInTwelveBits[channel] = int(self.pitchInTwelveBits[channel] + (pitchDifferenceInTwelveBits / 1 * positionAsDecimal))

					if self.slideCV1 == True:
						self.cv1InTwelveBits[channel] = int(self.cv1InTwelveBits[channel] + (cv1DifferenceInTwelveBits / 1 * positionAsDecimal))

					if self.slideCV2 == True:
						self.cv2InTwelveBits[channel] = int(self.cv2InTwelveBits[channel] + (cv2DifferenceInTwelveBits / 1 * positionAsDecimal))

		# Work out the current row's triggers
		triggers = self.triggerPattern[self.currentRowNumber]

		for i in range(8):
			if triggers & 1 << i: # "2 << i" basically means "Two to the power of i"
				self.triggerInTwelveBits[7 - i] = HIGH
			else:
				self.triggerInTwelveBits[7 - i] = LOW

		return incrementLengthInMicroseconds

	def loadPattern(self, filename):
		# Wipe the old pattern
		self.reset()

		# Load the new song
		try:
			song = open(filename, 'r')
		except IOError:
			# If the file doesn't exist yet, make a blank one.
			self.savePattern(filename)
			song = open(filename, 'r')

		# Load the tempo
		song.seek(3)
		self.tempo = ord(song.read(1))

		# Load the pattern length
		song.seek(4 + self.currentPatternNumber)
		self.numberOfRows = ord(song.read(1))

		# Seek ahead
		song.seek(4 + MAX_NUMBER_OF_PATTERNS + (self.currentPatternNumber * MAX_NUMBER_OF_ROWS * ((NUMBER_OF_CHANNELS * 5) + 1))) # 5 bytes per event, plus 1 byte per row for the triggers

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

			triggers = ord(song.read(1))
			self.triggerPattern[currentRowNumber] = triggers

		currentRowNumber = currentRowNumber + 1
		song.close()

	def pastePattern(self):
		self.patternInSixtieths = self.clipboard
		self.triggerPattern = self.triggerClipboard
		self.clipboard = []
		self.triggerClipboard = []
		self.clipboardFull = False

	def removeRow(self):
		if self.numberOfRows > 1:
			self.numberOfRows = self.numberOfRows - 1

			if self.currentRowNumber > self.numberOfRows - 1:
				self.currentRowNumber = self.numberOfRows - 1

			for channel in range(NUMBER_OF_CHANNELS):
				self.patternInSixtieths[self.numberOfRows][channel] = {'pitch': DEFAULT_PITCH, 'slide': 0, 'gate': 0, 'cv1': 0, 'cv2': 0} # Reset removed row to defaults, namely silent Cs.  We would add 1 to the number of rows, as we want to go one above it, but remember that us hackers count starting with 0.

	def reset(self):
		"""Clear the pattern held in memory."""
		self.tempo = DEFAULT_TEMPO
		self.numberOfRows = DEFAULT_NUMBER_OF_ROWS
		self.patternInSixtieths = []
		self.triggerPattern = []

		for row in range(MAX_NUMBER_OF_ROWS):
			self.patternInSixtieths.append([])
			self.triggerPattern.append([])

			for channel in range(NUMBER_OF_CHANNELS):
				self.patternInSixtieths[row].append([])
				self.patternInSixtieths[row][channel] = {'pitch': DEFAULT_PITCH, 'slide': 0, 'gate': 0, 'cv1': 0, 'cv2': 0} # Reset removed row to defaults, namely silent Cs

			self.triggerPattern[row] = 0

	def savePattern(self, filename):
		# Save the current song
		try:
			song = open(filename, 'r+') # If it already exists, open the file in read/write mode so seeking past some data won't blat those data.
		except IOError:
			song = open(filename, 'w') # If it doesn't already exist, create it first.

			# Write a whole file of defaults first
			song.write("ST1") # Stepper 1 format, codenamed "Hanley" (not yet finalised)
			song.write(chr(DEFAULT_TEMPO))

			for pattern in range(MAX_NUMBER_OF_PATTERNS):
				song.write(chr(DEFAULT_NUMBER_OF_ROWS))

			for row in range(MAX_NUMBER_OF_PATTERNS * MAX_NUMBER_OF_ROWS):
				for event in range(NUMBER_OF_CHANNELS):
					song.write(chr(DEFAULT_PITCH) + chr(0) + chr(0) + chr(0) + chr(0)) # Gate and CV

				song.write(chr(0)) # Triggers

			song.close()

			# Now re-open the file as normal
			song = open(filename, 'r+') # Now we know it already exists, open the file again, this time in read/write mode so seeking past some data won't blat those data.

		# Save the tempo
		song.seek(3)
		song.write(chr(self.tempo))

		# Save the pattern length
		song.seek(4 + self.currentPatternNumber)
		numberOfRows = chr(self.numberOfRows)
		song.write(numberOfRows)

		# Seek ahead
		song.seek(4 + MAX_NUMBER_OF_PATTERNS + (self.currentPatternNumber * MAX_NUMBER_OF_ROWS * ((NUMBER_OF_CHANNELS * 5) + 1))) # 5 bytes per event, plus 1 byte per row for the triggers

		# Save the current pattern
		for currentRowNumber in range(MAX_NUMBER_OF_ROWS):
			for currentChannelNumber in range(NUMBER_OF_CHANNELS):
				pitch = chr(self.patternInSixtieths[currentRowNumber][currentChannelNumber]['pitch'])
				slide = chr(self.patternInSixtieths[currentRowNumber][currentChannelNumber]['slide'])
				gate = chr(self.patternInSixtieths[currentRowNumber][currentChannelNumber]['gate'])
				cv1 = chr(self.patternInSixtieths[currentRowNumber][currentChannelNumber]['cv1'])
				cv2 = chr(self.patternInSixtieths[currentRowNumber][currentChannelNumber]['cv2'])
				song.write(pitch + slide + gate + cv1 + cv2)

			triggers = chr(self.triggerPattern[currentRowNumber])
			song.write(triggers)

		song.close()

	def setCV1(self, cv1):
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['cv1'] = cv1

	def setCV2(self, cv2):
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['cv2'] = cv2

	def setDinSyncGate(self, dinSyncGate):
		if self.dinSyncGateInputInTwelveBits == LOW and dinSyncGate == HIGH: # Transition to starting
			self.dinSyncGateInputInTwelveBits = dinSyncGate
			self.setPlayMode(self.lastPlayMode)
		elif self.dinSyncGateInputInTwelveBits == HIGH and dinSyncGate == LOW: # Transition to stopping
			self.dinSyncGateInputInTwelveBits = dinSyncGate
			self.setPlayMode(0)

	def setDinSyncTrigger(self, dinSyncTrigger):
		if self.dinSyncTriggerInputInTwelveBits == LOW and dinSyncTrigger == HIGH:
			self.dinSyncTriggerOutputLengthInMicroseconds = self.absoluteTimeInMicroseconds - self.absoluteLastDinSyncTriggerInputInMicroseconds # Update our clock to match theirs, based on the time between their last two DIN sync trigger inputs  (I need to tidy this up.  It will match the frequency, but not the phase/offset.)
			self.absoluteLastDinSyncTriggerInputInMicroseconds = self.absoluteTimeInMicroseconds
			self.averageRowLengthInMicroseconds = self.dinSyncTriggerOutputLengthInMicroseconds * PULSES_PER_QUARTER_NOTE / 4
			self.tempo = 60000000 / (self.averageRowLengthInMicroseconds * 4)

		self.dinSyncTriggerInputInTwelveBits = dinSyncTrigger

	def setGate(self, gate):
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['gate'] = gate

	def setOctave(self, octave):
		semitone = self.getSemitone()
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch'] = semitone + (octave * SEMITONES_IN_OCTAVE_INT)

	def setPitch(self, pitchInSixtieths):
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch'] = pitchInSixtieths

	def setPlayMode(self, playMode):
		self.playMode = playMode

		# Technically, nextPatternNumber and finalPatternNumber could probably be the same variable, but I wouldn't advise that as it would be needlessly confusing.
		if playMode == 0:
			self.queuedDinSyncGateOutput = LOW
			self.playTimeInMicroseconds = 0
			pass
		elif playMode == 1:
			self.queuedDinSyncGateOutput = HIGH
			self.patternPositionInMicroseconds = 0
			self.nextPatternNumber = self.currentPatternNumber # Play mode 1 will use this default, unless the user queues up a pattern change in the meantime.
			self.lastPlayMode = 1
		else:
			self.queuedDinSyncGateOutput = HIGH
			self.patternPositionInMicroseconds = 0
			self.finalPatternNumber = self.currentPatternNumber # Play modes 2 and 3 will use this.
			self.currentPatternNumber = 0
			self.lastPlayMode = 2 # Being a slave means we don't get to call the shots, even the one-shots.  We have to loop until we're told to stop.

	def setSemitone(self, semitone):
		octave = self.getOctave()
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch'] = semitone + (octave * SEMITONES_IN_OCTAVE_INT)

	def setSlide(self, slide):
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['slide'] = slide

	def setSwing(self, swing):
		self.swing = swing

	def setTempo(self, tempo):
		self.tempo = int(tempo)
		self.averageRowLengthInMicroseconds = 15000000 / self.tempo # 60 seconds per minute; 60 / BPM = crotchet length in seconds; 60,000,000 / BPM = crotchet length in microseconds; crotchet length in microseconds / 4 = semiquaver length in microseconds; 60,000,000 / 4 = 15,000,000; 15,000,000 / BPM = semiquaver length in microseconds; average row length = semiquaver length.
		self.dinSyncTriggerOutputLengthInMicroseconds = (60000000 / PULSES_PER_QUARTER_NOTE) / self.tempo # Quarter note = crotchet.

	def toggleTrigger(self, triggerChannel):
		self.triggerPattern[self.currentRowNumber] = self.triggerPattern[self.currentRowNumber]^ 1 << 8 - triggerChannel

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
