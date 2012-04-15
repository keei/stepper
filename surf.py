# Surf, version 0.1, for Python 3.
# By ZoeB, 2012-04-10 to 2012-04-15.

# This is a software implementation of a basic modular synthesiser.
# Almost all values should be numbers between either -5 and +5,
# or 0 and +5.  Theoretically, it should one day be possible to connect
# this application to real modular hardware.

from math import ceil, floor, pi, sin
from random import uniform
from struct import pack
from wave import open

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
	audioInBipolarVolts = 0.0                     # -5 to +5, float

	def __init__(self):
		pass

	def getAudio(self):
		return 0 - self.audioInBipolarVolts

	def setAudio(self, audioInBipolarVolts):
		self.audioInBipolarVolts = audioInBipolarVolts
		return True

class NoiseGenerator:
	def __init__(self):
		pass

	def getAudio(self):
		return uniform(-5, 5)

class Oscillator:
	centOffset = 0.0                # -5 to +5, float
	frequency = 0.0                 # 0 to unlimited, float
	octaveOffset = 0                # -5 to +5, int
	pointer = 0.0                   # 0 to +5, float
	pulseWidth = 0.0                # -5 to +5, float
	sineWaveLookupTable = []

	def __init__(self):
		i = 0

		while i < 1000:
			self.sineWaveLookupTable.append(sin(i / 1000 * 2 * pi) * 5)
			i = i + 1

	def getPulse(self):
		if self.pointer < self.pulseWidth:
			return 5
		else:
			return -5

	def getSine(self):
		pointer = int(floor((self.pointer + 5) * 100))
		return self.sineWaveLookupTable[pointer]

	def getSawtooth(self):
		return self.pointer

	def incrementTime(self, incrementLengthInSeconds):
		self.pointer = (self.pointer + 5) / 10 # From [-5 to +5] to [0 to +1]
		self.pointer = (self.pointer + (self.frequency * incrementLengthInSeconds)) % 1
		self.pointer = (self.pointer * 10) - 5 # From [0 to +1] to [-5 to +5]

	def setOctaveOffset(self, octaveOffset):
		self.octaveOffset = octaveOffset

	def setPitch(self, pitch):
		self.frequency = 440 / (2 ** 4.75) * (2 ** (pitch + self.octaveOffset + (self.centOffset / 5 * 100))) # A4 = 440Hz = 4.75v

	def setPulseWidth(self, pulseWidth):
		self.pulseWidth = pulseWidth

class Output:
	buffer = []
	filename = 'surf.wav'
	time = 0                        # 0 to unlimited, int
	valueLeft = 0.0                 # -5 to +5, float
	valueRight = 0.0                # -5 to +5, float
	writing = False                 # Boolean

	def __del__(self):
		self.stop()

	def __init__(self):
		pass

	def setFilename(self, filename):
		self.filename = filename

	def setValue(self, valueLeft, valueRight = None):
		self.valueLeft = valueLeft

		if valueRight != None:
			self.valueRight = valueRight
		else:
			self.valueRight = valueLeft

	def start(self):
		self.buffer = []
		self.writing = True

	def stop(self):
		# Only make CD quality files
		self.outputFile = open(self.filename, 'w')
		self.outputFile.setnchannels(2) # Stereo
		self.outputFile.setsampwidth(2) # 16-bit
		self.outputFile.setframerate(44100)

		valueBinary = bytes()
		valueBinary = valueBinary.join(self.buffer)
		self.outputFile.writeframes(valueBinary)

		self.outputFile.close()
		self.writing = False

	def write(self):
		if self.writing == False:
			self.start()

		valueLeft = int(floor(self.valueLeft / 5 * 32767)) # 16-bit
		valueBinary = pack('<h', valueLeft)
		self.buffer.append(valueBinary)
		valueRight = int(floor(self.valueRight / 5 * 32767)) # 16-bit
		valueBinary = pack('<h', valueRight)
		self.buffer.append(valueBinary)

class Sequencer:
	cv1InUnipolarVolts = []
	cv2InUnipolarVolts = []
	eventRowLengthInSeconds = 0.0
	eventRowNumber = 0
	eventRowPositionInIterations = 0
	eventRowPositionInSeconds = 0.0
	gateInUnipolarVolts = []
	matrix = []
	noteTable = ['C-', 'C#', 'D-', 'D#', 'E-', 'F-', 'F#', 'G-', 'G#', 'A-', 'A#', 'B-']
	numberOfChannels = 4
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

	tempo = 120.0
	matrixPositionInSeconds = 0.0

	def __init__(self):
		self.setTempo(120)            # Default to 120BPM
		self.setNumberOfChannels(4)   # Default to 4 channels
		self.eventRowPositionInIterations = 0 # If I ever make a "reset" method, it should do this!

	def addEventRow(self, eventRow):
		if not self.matrix:
			self.setNumberOfChannels(ceil(len(eventRow) / 16))

		self.matrix.append(eventRow)

	def getCV1(self, channel):
		return self.cv1InUnipolarVolts[channel]

	def getCV2(self, channel):
		return self.cv2InUnipolarVolts[channel]

	def getGate(self, channel):
		return self.gateInUnipolarVolts[channel]

	def getPitch(self, channel):
		return self.pitchInUnipolarVolts[channel]

	def getTrackLength(self):
		return len(self.matrix) * self.eventRowLengthInSeconds

	def getTime(self):
		return self.matrixPositionInSeconds

	def incrementTime(self):
		incrementLengthInSeconds = float(1) / float(44100)
		self.matrixPositionInSeconds = self.matrixPositionInSeconds + incrementLengthInSeconds

		# Work out the current event row
		eventRowNumber = int(self.matrixPositionInSeconds // self.eventRowLengthInSeconds)

		if eventRowNumber > len(self.matrix) - 1:
			eventRowNumber = len(self.matrix) - 1

		# See if we're up to a new event row, otherwise advance the iteration
		if eventRowNumber > self.eventRowNumber:
			self.eventRowNumber = eventRowNumber
			self.eventRowPositionInIterations = 0
		else:
			self.eventRowPositionInIterations = self.eventRowPositionInIterations + 1

		self.eventRowPositionInSeconds = self.eventRowPositionInIterations * incrementLengthInSeconds

		# Read in the current and next event rows
		eventRow = self.matrix[eventRowNumber]
		nextEventRowNumber = eventRowNumber + 1

		if nextEventRowNumber > len(self.matrix) - 1:
			nextEventRowNumber = len(self.matrix) - 1

		nextEventRow = self.matrix[nextEventRowNumber]

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
				gateLengthInSeconds = float(eventRow[(channel * 16) + 6:(channel * 16) + 8]) / float(99) * float(self.eventRowLengthInSeconds)
			elif slide == True:
				gateLengthInSeconds = self.eventRowLengthInSeconds
			elif eventRow[(channel * 16) + 0:(channel * 16) + 3] != '...':
				gateLengthInSeconds = self.eventRowLengthInSeconds / 2
			else:
				gateLengthInSeconds = 0.0

			# We need to make sure that we don't get any stray gate ons or gate offs, even for one single iteration
			if self.eventRowPositionInSeconds > gateLengthInSeconds or (self.eventRowPositionInSeconds == gateLengthInSeconds and gateLengthInSeconds == 0):
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
				nextNoteName = nextEventRow[(channel * 16) + 0:(channel * 16) + 3]
				nextPitchInUnipolarVolts = self.pitchVoltageLookupTable[nextNoteName]
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
				if self.eventRowPositionInSeconds > gateLengthInSeconds:
					pitchDifference = nextPitchInUnipolarVolts - self.pitchInUnipolarVolts[channel]
					cv1Difference = nextCV1InUnipolarVolts - self.cv1InUnipolarVolts[channel]
					cv2Difference = nextCV2InUnipolarVolts - self.cv2InUnipolarVolts[channel]

					# Work out how far along the slide we are, from 0 to 1
					beginningInSeconds = gateLengthInSeconds
					endInSeconds = self.eventRowLengthInSeconds
					positionInSeconds = self.eventRowPositionInSeconds
					offsetPositionInSeconds = positionInSeconds - beginningInSeconds
					offsetEndInSeconds = endInSeconds - beginningInSeconds
					positionAsDecimal = offsetPositionInSeconds / offsetEndInSeconds

					self.pitchInUnipolarVolts[channel] = self.pitchInUnipolarVolts[channel] + (pitchDifference / 1 * positionAsDecimal)
					self.cv1InUnipolarVolts[channel] = self.cv1InUnipolarVolts[channel] + (cv1Difference / 1 * positionAsDecimal)
					self.cv2InUnipolarVolts[channel] = self.cv2InUnipolarVolts[channel] + (cv2Difference / 1 * positionAsDecimal)

		return incrementLengthInSeconds

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

	def setTempo(self, tempo):
		self.tempo = float(tempo)
		crotchetLengthInSeconds = 60.0 / self.tempo
		semiquaverLengthInSeconds = crotchetLengthInSeconds / 4.0
		self.eventRowLengthInSeconds = semiquaverLengthInSeconds

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
		if self.cvInUnipolarVolts > 0 and self.gateInUnipolarVolts == 0:
			self.cvInUnipolarVolts = self.cvInUnipolarVolts - (incrementLengthInSeconds / self.speedInUnipolarVolts);

	def setGate(self, gateInUnipolarVolts):
			self.gateInUnipolarVolts = gateInUnipolarVolts

			if gateInUnipolarVolts == 5:
				self.cvInUnipolarVolts = gateInUnipolarVolts

	def setSpeed(self, speedInUnipolarVolts):
		self.speedInUnipolarVolts = speedInUnipolarVolts
