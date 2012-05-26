# Stepper 1 library, for Python 3.

# Pseudo-constants:

DEFAULT_PITCH = 24 # C-2
DEFAULT_TEMPO = 120

try:
	FILENAME
except NameError:
	FILENAME = 'stepper.stp'

FROM_TEMPO_TO_MILLISECONDS = 625 # 60 seconds per minute; 60 / BPM = quarter note length in seconds; 60,000 / BPM = quarter note length in milliseconds; quarter note length in milliseconds / 96 = clock pulse length in milliseconds; 60,000 / 96 = 625; 625 / BPM = pulse length in milliseconds
FROM_SIXTIETHS_TO_PULSES = 0.2 # Multiplying by 0.8 is the same as dividing by 60.0 and multiplying by 12, as in 12 PPSNs
FROM_SIXTIETHS_TO_TWELVE_BITS = 68.25 # Multiplying by 68.25 is the same as dividing by 60.0 and multiplying by 4095.0
HIGH = 4095
LOW = 0

try:
	MAX_NUMBER_OF_PATTERNS
except NameError:
	MAX_NUMBER_OF_PATTERNS = 64

try:
	MAX_NUMBER_OF_ROWS
except NameError:
	MAX_NUMBER_OF_ROWS = 64

SEMITONES_IN_OCTAVE_FLOAT = 12.0
SEMITONES_IN_OCTAVE_INT = 12
SEQUENCER_PPSN = 12 # 48 PPQN = 12 PPSN

class AcidSequencer:
	clipboard = []
	clipboardFull = False
	currentPatternNumber = 0
	currentRowNumber = 0
	accentInTwelveBits = 0
	gateInTwelveBits = 0
	lastRowNumber = 0
	nextPatternNumber = 0
	numberOfRows = 0
	patternInSixtieths = []
	pitchInTwelveBits = 1638 # C-2
	pulseCount = 0
	slideInTwelveBits = 0

	def __init__(self):
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

	def copyPattern(self):
		self.clipboard = self.patternInSixtieths
		self.clipboardFull = True

	def decrementCurrentPatternNumber(self):
		if self.currentPatternNumber > 0:
			self.currentPatternNumber = self.currentPatternNumber - 1
			self.loadPattern(FILENAME)

	def decrementCurrentRowNumber(self):
		if self.currentRowNumber > 0:
			self.currentRowNumber = self.currentRowNumber - 1

	def decrementNextPatternNumber(self):
		if self.nextPatternNumber > 0:
			self.nextPatternNumber = self.currentPatternNumber - 1

	def getClipboardStatus(self):
		return self.clipboardFull

	def getCurrentPatternNumber(self):
		return self.currentPatternNumber

	def getCurrentRowNumber(self):
		return self.currentRowNumber

	def getAccentInSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber]['accent']

	def getAccentInTwelveBits(self):
		return self.accentInTwelveBits

	def getGateInSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber]['gate']

	def getGateInTwelveBits(self):
		return self.gateInTwelveBits

	def getOctave(self):
		return int(float(self.patternInSixtieths[self.currentRowNumber]['pitch']) / SEMITONES_IN_OCTAVE_FLOAT)

	def getPatternLength(self):
		return self.numberOfRows

	def getPitchInSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber]['pitch']

	def getPitchInTwelveBits(self):
		return self.pitchInTwelveBits

	def getSemitone(self):
		return self.patternInSixtieths[self.currentRowNumber]['pitch'] % SEMITONES_IN_OCTAVE_INT

	def getSlideInSixtieths(self):
		return self.patternInSixtieths[self.currentRowNumber]['slide']

	def getSlideInTwelveBits(self):
		return self.slideInTwelveBits

	def incrementCurrentPatternNumber(self):
		if self.currentPatternNumber < MAX_NUMBER_OF_PATTERNS - 1: # Count starting 0
			self.currentPatternNumber = self.currentPatternNumber + 1
			self.loadPattern(FILENAME)

	def incrementCurrentRowNumber(self):
		if self.currentRowNumber < self.numberOfRows - 1:
			self.currentRowNumber = self.currentRowNumber + 1

	def incrementNextPatternNumber(self):
		if self.nextPatternNumber != MAX_NUMBER_OF_PATTERNS - 1: # Count starting 0
			self.nextPatternNumber = self.nextPatternNumber + 1

	def incrementPulseCount(self):
		self.pulseCount = self.pulseCount + 1

		# At the end of the pattern, loop back around to the beginning
		if self.pulseCount >= SEQUENCER_PPSN * self.numberOfRows:
			self.pulseCount = 0
			self.currentPatternNumber = self.nextPatternNumber
			self.loadPattern(FILENAME)

		# Work out which row we're on.  If it's changed, note the last row we were on, for slides.
		newCurrentRowNumber = int(self.pulseCount / SEQUENCER_PPSN)

		if newCurrentRowNumber != self.currentRowNumber:
			self.lastRowNumber = self.currentRowNumber

		self.currentRowNumber = newCurrentRowNumber

		# Work out the current event's pitch, slide, gate length and accent
		# Convert the pitch to a control voltage, 1v/oct
		pitchInSixtieths = self.patternInSixtieths[self.currentRowNumber]['pitch']
		self.pitchInTwelveBits = int(float(pitchInSixtieths) * FROM_SIXTIETHS_TO_TWELVE_BITS)

		# I should reprogram this so that the slide number controls the amount of slew, the speed of the portamento
		if self.patternInSixtieths[self.lastRowNumber]['slide'] == 0:
			self.slideInTwelveBits = LOW
		else:
			self.slideInTwelveBits = HIGH

		# Set the gate length
		gateInSixtieths = self.patternInSixtieths[self.currentRowNumber]['gate']
		gateLengthInPulses = int(float(gateInSixtieths) * FROM_SIXTIETHS_TO_PULSES)

		if self.pulseCount % SEQUENCER_PPSN < gateLengthInPulses:
			self.gateInTwelveBits = HIGH
		else:
			self.gateInTwelveBits = LOW

		# Set the accent
		accentInSixtieths = self.patternInSixtieths[self.currentRowNumber]['accent']
		self.accentInTwelveBits = int(float(accentInSixtieths) * FROM_SIXTIETHS_TO_TWELVE_BITS)

		return

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

		# Load the pattern length
		song.seek(3 + self.currentPatternNumber)
		self.numberOfRows = ord(song.read(1))

		# Seek ahead
		song.seek(3 + MAX_NUMBER_OF_PATTERNS + (self.currentPatternNumber * MAX_NUMBER_OF_ROWS * 4))

		# Load the current pattern
		for currentRowNumber in range(MAX_NUMBER_OF_ROWS):
			firstByte = song.read(1)

			if not firstByte: # End of file.  Nothing to load.  This pattern doesn't exist yet.
				return

			pitch = ord(firstByte)
			slide = ord(song.read(1))
			gate = ord(song.read(1))
			accent = ord(song.read(1))

			self.patternInSixtieths[currentRowNumber]['pitch'] = pitch
			self.patternInSixtieths[currentRowNumber]['slide'] = slide
			self.patternInSixtieths[currentRowNumber]['gate'] = gate
			self.patternInSixtieths[currentRowNumber]['accent'] = accent

		song.close()

	def pastePattern(self):
		self.patternInSixtieths = self.clipboard
		self.clipboard = []
		self.clipboardFull = False

	def removeRow(self):
		if self.numberOfRows > 1:
			self.numberOfRows = self.numberOfRows - 1

			if self.currentRowNumber > self.numberOfRows - 1:
				self.currentRowNumber = self.numberOfRows - 1

			self.patternInSixtieths[self.numberOfRows] = {'pitch': DEFAULT_PITCH, 'slide': 0, 'gate': 0, 'accent': 0} # Reset removed row to defaults, namely silent Cs.  We would add 1 to the number of rows, as we want to go one above it, but remember that us hackers count starting with 0.

	def reset(self):
		"""Clear the pattern held in memory."""
		self.numberOfRows = DEFAULT_NUMBER_OF_ROWS
		self.patternInSixtieths = []

		for row in range(MAX_NUMBER_OF_ROWS):
			self.patternInSixtieths.append([])
			self.patternInSixtieths[row].append([])
			self.patternInSixtieths[row] = {'pitch': DEFAULT_PITCH, 'slide': 0, 'gate': 0, 'accent': 0} # Reset removed row to defaults, namely silent Cs

	def resetPulseCount(self):
		self.pulseCount = (48 * self.numberOfRows) - 1 # The next time the pulse is incremented, it'll flip back over to 0

	def savePattern(self, filename):
		# Save the current song
		try:
			song = open(filename, 'r+') # If it already exists, open the file in read/write mode so seeking past some data won't blat those data.
		except IOError:
			song = open(filename, 'w') # If it doesn't already exist, create it first.

			# Write a whole file of defaults first
			song.write("SA1") # Stepper 1 format, codenamed "Swansea" (not yet finalised)

			for pattern in range(MAX_NUMBER_OF_PATTERNS):
				song.write(chr(DEFAULT_NUMBER_OF_ROWS))

			for row in range(MAX_NUMBER_OF_PATTERNS * MAX_NUMBER_OF_ROWS):
				song.write(chr(DEFAULT_PITCH) + chr(0) + chr(0) + chr(0)) # Gate and CV

			song.close()

			# Now re-open the file as normal
			song = open(filename, 'r+') # Now we know it already exists, open the file again, this time in read/write mode so seeking past some data won't blat those data.

		# Save the pattern length
		song.seek(3 + self.currentPatternNumber)
		numberOfRows = chr(self.numberOfRows)
		song.write(numberOfRows)

		# Seek ahead
		song.seek(3 + MAX_NUMBER_OF_PATTERNS + (self.currentPatternNumber * MAX_NUMBER_OF_ROWS * 4))

		# Save the current pattern
		for currentRowNumber in range(MAX_NUMBER_OF_ROWS):
			pitch = chr(self.patternInSixtieths[currentRowNumber]['pitch'])
			slide = chr(self.patternInSixtieths[currentRowNumber]['slide'])
			gate = chr(self.patternInSixtieths[currentRowNumber]['gate'])
			accent = chr(self.patternInSixtieths[currentRowNumber]['accent'])
			song.write(pitch + slide + gate + accent)

		song.close()

	def setAccent(self, accent):
		self.patternInSixtieths[self.currentRowNumber]['accent'] = accent

	def setGate(self, gate):
		self.patternInSixtieths[self.currentRowNumber]['gate'] = gate

	def setNextPatternNumber(self, nextPatternNumber):
		self.nextPatternNumber = nextPatternNumber

	def setOctave(self, octave):
		semitone = self.getSemitone()
		self.patternInSixtieths[self.currentRowNumber]['pitch'] = semitone + (octave * SEMITONES_IN_OCTAVE_INT)

	def setPitch(self, pitchInSixtieths):
		self.patternInSixtieths[self.currentRowNumber]['pitch'] = pitchInSixtieths

	def setSemitone(self, semitone):
		octave = self.getOctave()
		self.patternInSixtieths[self.currentRowNumber]['pitch'] = semitone + (octave * SEMITONES_IN_OCTAVE_INT)

	def setSlide(self, slide):
		self.patternInSixtieths[self.currentRowNumber]['slide'] = slide

	def transposePatternDown(self):
		# Only transpose down if every note in the pattern will still be in the 0 to 60 range afterwards
		lowestPitch = 60

		for row in self.patternInSixtieths:
			if row['pitch'] < lowestPitch:
				lowestPitch = row['pitch']

		if lowestPitch == 0:
			return

		# Go ahead and transpose the pattern
		for row in self.patternInSixtieths:
			row['pitch'] = row['pitch'] - 1

	def transposePatternUp(self):
		# Only transpose up if every note in the pattern will still be in the 0 to 60 range afterwards
		highestPitch = 0

		for row in self.patternInSixtieths:
			if row['pitch'] > highestPitch:
				highestPitch = row['pitch']

		if highestPitch == 60:
			return

		# Go ahead and transpose the pattern
		for row in self.patternInSixtieths:
			row['pitch'] = row['pitch'] + 1

class Clock:
	lastTime = 0 # When the last pulse started, in milliseconds
	pulseLength = 5 # The amount of time between one pulse start and the next, in milliseconds
	runRequest = LOW # Whether or not we're about to run
	run = LOW # Whether or not we're running
	pulse = LOW # The clock pulse, 96 PPQN.  Count 1 in 2 for 48 PPQN, or 1 in 4 for 24 PPQN.
	tempo = DEFAULT_TEMPO # In BPM

	def decrementTempo(self):
		if self.tempo > 1:
			self.setTempo(self.tempo - 1)

	def getPulse(self):
		return self.pulse

	def getRun(self):
		return self.run

	def getRunRequest(self):
		return self.runRequest

	def getTempo(self):
		return self.tempo

	def incrementTempo(self):
		if self.tempo < 255:
			self.setTempo(self.tempo + 1)

	def setRunRequest(self, runRequest): # Press the run/stop button
		self.runRequest = runRequest

	def setTempo(self, tempo):
		self.tempo = tempo
		self.pulseLength = int(FROM_TEMPO_TO_MILLISECONDS / self.tempo)

	def setTime(self, time):
		# The pulse has a duty cycle of 50%.  Let's use simple modulo arithmetic.
		if (time - self.lastTime) < (self.pulseLength / 2):
			self.pulse = HIGH # The last pulse is still happening
		elif (time - self.lastTime) > self.pulseLength:
			self.pulse = HIGH # The next pulse is already happening
			self.lastTime = time

			if self.runRequest == HIGH:
				self.run = HIGH
			else:
				self.run = LOW
		else:
			self.pulse = LOW # Neither pulse is happening

class DrumSequencer:
	clipboard = []
	clipboardFull = False
	currentPatternNumber = 0
	currentRowNumber = 0
	nextPatternNumber = 0
	numberOfRows = 0
	pattern = []
	pulseCount = 0
	triggerInTwelveBits = []

	def __init__(self):
		for channel in range(8):
			self.triggerInTwelveBits.append(LOW)

		self.reset()

	def addRow(self):
		if self.numberOfRows < MAX_NUMBER_OF_ROWS:
			self.numberOfRows = self.numberOfRows + 1

	def convertNumberIntoChars(self, number):
		"""Convert a number into three characters, suitable for display on an LCD."""
		number = int(number)
		number = '%03d' % number
		return number

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
		self.clipboard = self.pattern
		self.clipboardFull = True

	def decrementCurrentPatternNumber(self):
		if self.currentPatternNumber > 0:
			self.currentPatternNumber = self.currentPatternNumber - 1
			self.loadPattern(FILENAME)

	def decrementCurrentRowNumber(self):
		if self.currentRowNumber > 0:
			self.currentRowNumber = self.currentRowNumber - 1

	def decrementNextPatternNumber(self):
		if self.nextPatternNumber > 0:
			self.nextPatternNumber = self.currentPatternNumber - 1

	def getClipboardStatus(self):
		return self.clipboardFull

	def getCurrentPatternNumber(self):
		return self.currentPatternNumber

	def getCurrentRowNumber(self):
		return self.currentRowNumber

	def getPatternLength(self):
		return self.numberOfRows

	def getTriggerInTwelveBits(self, channel):
		return self.triggerInTwelveBits[channel]

	def incrementCurrentPatternNumber(self):
		if self.currentPatternNumber < MAX_NUMBER_OF_PATTERNS - 1: # Count starting 0
			self.currentPatternNumber = self.currentPatternNumber + 1
			self.loadPattern(FILENAME)

	def incrementCurrentRowNumber(self):
		if self.currentRowNumber < self.numberOfRows - 1:
			self.currentRowNumber = self.currentRowNumber + 1

	def incrementNextPatternNumber(self):
		if self.nextPatternNumber != MAX_NUMBER_OF_PATTERNS - 1: # Count starting 0
			self.nextPatternNumber = self.nextPatternNumber + 1

	def incrementPulseCount(self):
		self.pulseCount = self.pulseCount + 1

		# At the end of the pattern, loop back around to the beginning
		if self.pulseCount >= SEQUENCER_PPSN * self.numberOfRows:
			self.pulseCount = 0
			self.currentPatternNumber = self.nextPatternNumber
			self.loadPattern(FILENAME)

		self.currentRowNumber = int(self.pulseCount / SEQUENCER_PPSN)

		# Work out the current row's triggers
		if self.pulseCount % SEQUENCER_PPSN > SEQUENCER_PPSN / 2:
			for i in range(8):
				self.triggerInTwelveBits[i] = LOW
		else:
			triggers = self.pattern[self.currentRowNumber]

			for i in range(8):
				if triggers & 1 << i: # "2 << i" basically means "Two to the power of i"
					self.triggerInTwelveBits[7 - i] = HIGH
				else:
					self.triggerInTwelveBits[7 - i] = LOW

		return

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

		# Load the pattern length
		song.seek(3 + self.currentPatternNumber)
		self.numberOfRows = ord(song.read(1))

		# Seek ahead
		song.seek(3 + MAX_NUMBER_OF_PATTERNS + (self.currentPatternNumber * MAX_NUMBER_OF_ROWS))

		# Load the current pattern
		for currentRowNumber in range(MAX_NUMBER_OF_ROWS):
			triggers = ord(song.read(1))

			if not triggers: # End of file.  Nothing to load.  This pattern doesn't exist yet.
				return

			self.pattern[currentRowNumber] = triggers

		song.close()

	def pastePattern(self):
		self.pattern = self.clipboard
		self.clipboard = []
		self.clipboardFull = False

	def removeRow(self):
		if self.numberOfRows > 1:
			self.numberOfRows = self.numberOfRows - 1

			if self.currentRowNumber > self.numberOfRows - 1:
				self.currentRowNumber = self.numberOfRows - 1

		# The removed row's triggers should all be reset to off

	def reset(self):
		"""Clear the pattern held in memory."""
		self.numberOfRows = DEFAULT_NUMBER_OF_ROWS
		self.pattern = []

		for row in range(MAX_NUMBER_OF_ROWS):
			self.pattern.append(0)

	def resetPulseCount(self):
		self.pulseCount = (48 * self.numberOfRows) - 1 # The next time the pulse is incremented, it'll flip back over to 0

	def savePattern(self, filename):
		# Save the current song
		try:
			song = open(filename, 'r+') # If it already exists, open the file in read/write mode so seeking past some data won't blat those data.
		except IOError:
			song = open(filename, 'w') # If it doesn't already exist, create it first.

			# Write a whole file of defaults first
			song.write("SD1") # Stepper 1 format, codenamed "Shingle" (not yet finalised)

			for pattern in range(MAX_NUMBER_OF_PATTERNS):
				song.write(chr(DEFAULT_NUMBER_OF_ROWS))

			for row in range(MAX_NUMBER_OF_PATTERNS * MAX_NUMBER_OF_ROWS):
				song.write(chr(0))

			song.close()

			# Now re-open the file as normal
			song = open(filename, 'r+') # Now we know it already exists, open the file again, this time in read/write mode so seeking past some data won't blat those data.

		# Save the pattern length
		song.seek(3 + self.currentPatternNumber)
		numberOfRows = chr(self.numberOfRows)
		song.write(numberOfRows)

		# Seek ahead
		song.seek(3 + MAX_NUMBER_OF_PATTERNS + (self.currentPatternNumber * MAX_NUMBER_OF_ROWS))

		# Save the current pattern
		for currentRowNumber in range(MAX_NUMBER_OF_ROWS):
			triggers = chr(self.pattern[currentRowNumber])
			song.write(triggers)

		song.close()

	def setNextPatternNumber(self, nextPatternNumber):
		self.nextPatternNumber = nextPatternNumber

	def toggleTrigger(self, channel):
		self.pattern[self.currentRowNumber] = self.pattern[self.currentRowNumber]^ 1 << 8 - (channel + 1)

class SlewLimiter:
	lastTime = 0 # When the slew limiter was last invoked, in milliseconds
	pitchInTwelveBits = 0

	def getPitchInTwelveBits(self):
		return self.pitchInTwelveBits

	def setPitch(self, newPitchInTwelveBits, lag, milliseconds):
		interval = milliseconds - self.lastTime
		self.lastTime = milliseconds

		if lag == LOW:
			self.pitchInTwelveBits = newPitchInTwelveBits
		else:
			if newPitchInTwelveBits > self.pitchInTwelveBits + (interval * 2):
				self.pitchInTwelveBits = self.pitchInTwelveBits + interval
			elif newPitchInTwelveBits < self.pitchInTwelveBits - (interval * 2):
				self.pitchInTwelveBits = self.pitchInTwelveBits - interval
			else:
				self.pitchInTwelveBits = interval
