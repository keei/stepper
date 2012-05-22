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
	absoluteTimeInMilliseconds = 0
	averageRowLengthInMilliseconds = 0
	clipboard = []
	clipboardFull = False
	currentChannelNumber = 0
	currentPatternNumber = 0
	currentRowNumber = 0
	cv1InTwelveBits = []
	cv2InTwelveBits = []
	finalPatternNumber = 0 # Final in the context of looping / playing
	gateInTwelveBits = []
	nextPatternNumber = 0
	numberOfRows = 0
	patternPositionInMilliseconds = 0
	patternInSixtieths = []
	pitchInTwelveBits = []
	playMode = 0
	playTimeInMilliseconds = 0
	queuedSyncGate = LOW # What the sync gate (run/stop) should be at the time of the next sync trigger (clock pulse).  I'm guessing it needs to patiently wait until the next one, so let's do that.
	slideCV1 = True
	slideCV2 = True
	slidePitch = True
	swing = 0 # In the range of -127 to +127, in other words a signed char in C.
	syncGateInTwelveBits = LOW
	syncTriggerInTwelveBits = LOW
	syncTriggerLengthInMilliseconds = 1000
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
		return self.absoluteTimeInMilliseconds

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
		return self.playTimeInMilliseconds

	def getSemitone(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch'] % SEMITONES_IN_OCTAVE_INT

	def getSlideInSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['slide']

	def getSwing(self):
		return self.swing

	def getSyncGateInTwelveBits(self):
		return self.syncGateInTwelveBits

	def getSyncTriggerInTwelveBits(self):
		return self.syncTriggerInTwelveBits

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

	def incrementTime(self, incrementLengthInMilliseconds):
		# Send out a sync trigger as appropriate, even if we're paused
		self.absoluteTimeInMilliseconds = self.absoluteTimeInMilliseconds + incrementLengthInMilliseconds

		# The sync trigger (clock pulse) has a duty cycle of 50%.  Let's use simple modulo arithmetic.
		if self.absoluteTimeInMilliseconds % self.syncTriggerLengthInMilliseconds < self.syncTriggerLengthInMilliseconds / 2:
			# If the sync trigger's making the transition from low to high RIGHT NOW, then it's the first iteration of the loop during this clock cycle.  That's the only time we can change whether we're playing or paused, for bang on timing.
			if self.syncTriggerInTwelveBits == LOW:
				if self.queuedSyncGate == HIGH:
					self.syncGateInTwelveBits = HIGH
				else:
					self.syncGateInTwelveBits = LOW

			self.syncTriggerInTwelveBits = HIGH

		else:
			self.syncTriggerInTwelveBits = LOW
		
		# Play the pattern only if we're playing
		if self.syncGateInTwelveBits == LOW:
			return

		self.playTimeInMilliseconds = self.playTimeInMilliseconds + incrementLengthInMilliseconds
		self.patternPositionInMilliseconds = self.patternPositionInMilliseconds + incrementLengthInMilliseconds
		rowPairLengthInMilliseconds = self.averageRowLengthInMilliseconds * 2

		# Work out the current event row
		rowPairNumber = int(self.patternPositionInMilliseconds // rowPairLengthInMilliseconds)
		currentRowNumber = rowPairNumber * 2

		swingAsDecimal = (self.swing + 127.0) / 254.0
		firstRowLengthInMilliseconds = self.averageRowLengthInMilliseconds / 0.5 * swingAsDecimal
		rowPairPositionInMilliseconds = self.patternPositionInMilliseconds - (rowPairLengthInMilliseconds * rowPairNumber)

		if rowPairPositionInMilliseconds > firstRowLengthInMilliseconds:
			currentRowNumber = currentRowNumber + 1
			rowLengthInMilliseconds = rowPairLengthInMilliseconds - firstRowLengthInMilliseconds
			rowPositionInMilliseconds = rowPairPositionInMilliseconds - firstRowLengthInMilliseconds
		else:
			rowLengthInMilliseconds = firstRowLengthInMilliseconds
			rowPositionInMilliseconds = rowPairPositionInMilliseconds

		if currentRowNumber > self.numberOfRows - 1:
			self.patternPositionInMilliseconds = 0

			# It doesn't look like we can continue on to the next iteration of the loop, so let's just reset everything to 0 instead, which is what would happen anyway.
			currentRowNumber = 0
			rowPairNumber = 0
			rowPairPositionInMilliseconds = 0
			rowPositionInMilliseconds = 0

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
					self.queuedSyncGate = LOW
					self.playTimeInMilliseconds = 0

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
			gateLengthInMilliseconds = int(float(gateInSixtieths) / 60.0 * float(rowLengthInMilliseconds))

			# We need to make sure that we don't get any stray gate ons or gate offs, even for one single iteration
			if rowPositionInMilliseconds > gateLengthInMilliseconds or (rowPositionInMilliseconds == gateLengthInMilliseconds and gateLengthInMilliseconds == 0):
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
				if rowPositionInMilliseconds > rowLengthInMilliseconds / 2:
					pitchDifferenceInTwelveBits = nextPitchInTwelveBits - self.pitchInTwelveBits[channel]
					cv1DifferenceInTwelveBits = nextCV1InTwelveBits - self.cv1InTwelveBits[channel]
					cv2DifferenceInTwelveBits = nextCV2InTwelveBits - self.cv2InTwelveBits[channel]

					# Work out how far along the slide we are, from 0 to 1
					beginningInMilliseconds = rowLengthInMilliseconds / 2
					positionAsDecimal = (rowPositionInMilliseconds - beginningInMilliseconds) / (rowLengthInMilliseconds - beginningInMilliseconds)

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

		return incrementLengthInMilliseconds

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
			self.queuedSyncGate = LOW
			self.playTimeInMilliseconds = 0
			pass
		elif playMode == 1:
			self.queuedSyncGate = HIGH
			self.patternPositionInMilliseconds = 0
			self.nextPatternNumber = self.currentPatternNumber # Play mode 1 will use this default, unless the user queues up a pattern change in the meantime.
		else:
			self.queuedSyncGate = HIGH
			self.patternPositionInMilliseconds = 0
			self.finalPatternNumber = self.currentPatternNumber # Play modes 2 and 3 will use this.
			self.currentPatternNumber = 0

	def setSemitone(self, semitone):
		octave = self.getOctave()
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['pitch'] = semitone + (octave * SEMITONES_IN_OCTAVE_INT)

	def setSlide(self, slide):
		self.patternInSixtieths[self.currentRowNumber][self.currentChannelNumber]['slide'] = slide

	def setSwing(self, swing):
		self.swing = swing

	def setTempo(self, tempo):
		self.tempo = int(tempo)
		self.averageRowLengthInMilliseconds = 15000 / self.tempo # 60 seconds per minute; 60 / BPM = crotchet length in seconds; 60,000 / BPM = crotchet length in milliseconds; crotchet length in milliseconds / 4 = semiquaver length in milliseconds; 60,000 / 4 = 15,000; 15,000 / BPM = semiquaver length in milliseconds; average row length = semiquaver length.
		self.syncTriggerLengthInMilliseconds = (60000 / PULSES_PER_QUARTER_NOTE) / self.tempo # Quarter note = crotchet.

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
