# Surf, version 0.1, for Python 3.
# By ZoeB, 2012-04-10 to 2012-04-12.

# This is a software implementation of a basic modular synthesiser.
# Almost all values should be numbers between either -5 and +5,
# or 0 and +5.  Theoretically, it should one day be possible to connect
# this application to real modular hardware.

from math import ceil, floor, pi, sin
from struct import pack
import wave

class Attenuator:
	audio = 0.0                     # -5 to +5, float
	cv1 = 0.0                       # -5 to +5, float
	cv2 = 0.0                       # -5 to +5, float

	def __init__(self):
		pass

	def getAudio(self):
		return self.audio / 25 * self.cv1 * self.cv2

	def setAudio(self, audio):
		self.audio = audio
		return True

	def setCV1(self, cv1):
		self.cv1 = cv1
		return True

	def setCV2(self, cv2):
		self.cv2 = cv2
		return True

class DecayEnvelopeGenerator:
	cv = 0.0                        # 0 to +5, float
	gate = 0.0                      # 0 or +5, float
	speed = 0.1                     # 0 to +5, float

	def __init__(self):
		self.gate = 0.0
		self.speed = 0.1

	def getCV(self):
		return self.cv

	def incrementTime(self, increment):
		if self.cv > 0:
			self.cv = self.cv - (increment / self.speed);

	def setGate(self, gate):
		if self.gate == 0 and gate == 5:
			self.cv = 5
			self.gate = 5
		else:
			self.gate = gate

	def setSpeed(self, speed):
		self.speed = speed

class Inverter:
	audio = 0.0                     # -5 to +5, float

	def __init__(self):
		pass

	def getAudio(self):
		return 0 - self.audio

	def setAudio(self, audio):
		self.audio = audio
		return True

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
			return -1

	def getSine(self):
		pointer = int(floor((self.pointer + 5) * 100))
		return self.sineWaveLookupTable[pointer]

	def getSawtooth(self):
		return self.pointer

	def incrementTime(self, increment):
		self.pointer = (self.pointer + 5) / 10 # From [-5 to +5] to [0 to +1]
		self.pointer = (self.pointer + (self.frequency * increment)) % 1
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
		self.outputFile = wave.open(self.filename, 'w')
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
	cv1 = []                        # 0 to +5, float
	cv2 = []                        # 0 to +5, float
	gate = []                       # 0 or +5, float
	pitch = []                      # 0 to +5, float
	gateLength = 0.0                # -5 to +5, float
	noteRowNumber = 0               # 0 to unlimited, int
	noteRowTime = 0.0               # 0 to unlimited, float
	noteRows = []                   # Unlimited list of strings
	noteTable = ['C-', 'C#', 'D-', 'D#', 'E-', 'F-', 'F#', 'G-', 'G#', 'A-', 'A#', 'B-']
	noteRowLength = 0.0             # 0 to unlimited, float
	numberOfChannels = 4            # 0 to unlimited, int
	temperament = '12e'             # '12e'
	tempo = 120.0                   # 0 to unlimited, float
	time = 0.0                      # 0 to self.getTrackLength(), float

	def __init__(self):
		self.setTempo(120)            # Default to 120BPM
		self.setGateLength(0.0)       # Default to half the note length
		self.setNumberOfChannels(4)   # Default to 4 channels

	def addNoteRow(self, noteRow):
		if not self.noteRows:
			self.setNumberOfChannels(ceil(len(noteRow) / 16))

		self.noteRows.append(noteRow)

	def getCV1(self, channel):
		return self.cv1[channel]

	def getCV2(self, channel):
		return self.cv2[channel]

	def getGate(self, channel):
		return self.gate[channel]

	def getPitch(self, channel):
		return self.pitch[channel]

	def getTrackLength(self):
		return len(self.noteRows) * self.noteRowLength

	def getTime(self):
		return self.time

	def incrementTime(self):
		increment = float(1) / float(44100)
		self.time = self.time + increment

		# Work out the current note
		noteRowNumber = int(self.time // self.noteRowLength)

		if noteRowNumber > len(self.noteRows) - 1:
			noteRowNumber = len(self.noteRows) - 1

		# See if we're up to a new note (or rest)
		if noteRowNumber > self.noteRowNumber:
			self.noteRowNumber = noteRowNumber
			self.noteRowTime = 0.0
		else:
			self.noteRowTime = self.noteRowTime + increment

		for channel in range(self.numberOfChannels):
			# Work out each current note's pitch
			noteRow = self.noteRows[noteRowNumber]

			# Convert this pitch to a control voltage, 1v/oct
			if noteRow[(channel * 16) + 4:(channel * 16) + 5] == 'S':
				slide = True
				nextNoteRowNumber = noteRowNumber + 1

				if nextNoteRowNumber > len(self.noteRows) - 1:
					nextNoteRowNumber = len(self.noteRows) - 1

				nextNoteRow = self.noteRows[nextNoteRowNumber]

				if nextNoteRow[(channel * 16) + 0:(channel * 16) + 3] == '...':
					slide = False
			else:
				slide = False

			if noteRow[(channel * 16) + 0:(channel * 16) + 3] == '...':
				self.gate[channel] = 0.0
				self.noteRowTime = 0.0
			elif self.temperament == '12e':
				gateLength = (self.gateLength + 5) / 10 * self.noteRowLength

				if self.noteRowTime > gateLength and slide == False:
					self.gate[channel] = 0.0
				else:
					self.gate[channel] = 5

				noteLetter = noteRow[(channel * 16) + 0:(channel * 16) + 2]
				noteOctave = int(noteRow[(channel * 16) + 2:(channel * 16) + 3])
				noteOctave = noteOctave - 1
				noteNumber = self.noteTable.index(noteLetter)
				self.pitch[channel] = noteOctave + (1 / 12 * noteNumber) # I should check if I need to make any of these explicitly floats on some setups.
				noteCV1 = noteRow[(channel * 16) + 6:(channel * 16) + 9]
				self.cv1[channel] = float(noteCV1) / float(999) * float(5)
				noteCV2 = noteRow[(channel * 16) + 10:(channel * 16) + 13]
				self.cv2[channel] = float(noteCV2) / float(999) * float(5)
			else:
				pass

			if slide == True:
				if self.temperament == '12e':
					nextNoteLetter = nextNoteRow[(channel * 16) + 0:(channel * 16) + 2]
					nextNoteOctave = int(nextNoteRow[(channel * 16) + 2:(channel * 16) + 3])
					nextNoteOctave = nextNoteOctave - 1
					nextNoteNumber = self.noteTable.index(nextNoteLetter)
					nextPitch = nextNoteOctave + (1 / 12 * nextNoteNumber) # I should check if I need to make any of these explicitly floats on some setups.

					# Glide effortlessly and gracefully from self.pitch to nextPitch
					if self.noteRowTime > gateLength:
						difference = nextPitch - self.pitch[channel]

						# Work out how far along the slide we are, from 0 to 1
						beginning = gateLength
						end = self.noteRowLength
						time = self.noteRowTime
						time = time - beginning
						end = end - beginning
						time = time / end

						self.pitch[channel] = self.pitch[channel] + (difference / 1 * time)
				else:
					pass

		return increment

	def setGateLength(self, gateLength):
		self.gateLength = float(gateLength)

	def setNumberOfChannels(self, numberOfChannels):
		self.cv1 = []
		self.cv2 = []
		self.gate = []
		self.pitch = []

		for channel in range(numberOfChannels):
			self.cv1.append(0.0)
			self.cv2.append(0.0)
			self.gate.append(0.0)
			self.pitch.append(0.0)

		self.numberOfChannels = numberOfChannels
		return True

	def setTempo(self, tempo):
		self.tempo = float(tempo)
		crotchetLength = 60 / self.tempo
		semiquaverLength = crotchetLength / 4
		self.noteRowLength = semiquaverLength
