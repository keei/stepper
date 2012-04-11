# Surf, version 0.1, for Python 3.
# By ZoeB, 2012-04-10 to 2012-04-11.

# This is a software implementation of a basic modular synthesiser.
# Almost all values should be numbers between either -5 and +5,
# or 0 and +5.  Theoretically, it should one day be possible to connect
# this application to real modular hardware.

from math import floor, pi, sin
from struct import pack
import wave

class Attenuator:
	audio = 0                       # -5 to +5, float
	cv1 = 0                         # -5 to +5, float
	cv2 = 0                         # -5 to +5, float

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

class Oscillator:
	centOffset = 0                  # -5 to +5, float
	frequency = 0                   # 0 to +5, float
	octaveOffset = 0                # -5 to +5, int
	pointer = 0                     # 0 to +5, float
	pulseWidth = 0                  # -5 to +5, float
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
	filename = 'surf.wav'
	time = 0                        # 0 to unlimited, int
	valueLeft = 0                   # -5 to +5, float
	valueRight = 0                  # -5 to +5, float
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
		# Only make CD quality files
		self.outputFile = wave.open(self.filename, 'w')
		self.outputFile.setnchannels(2) # Stereo
		self.outputFile.setsampwidth(2) # 16-bit
		self.outputFile.setframerate(44100)
		self.writing = True

	def stop(self):
		self.outputFile.close()
		self.writing = False

	def write(self):
		if self.writing == False:
			self.start()

		valueLeft = int(floor(self.valueLeft / 5 * 32767)) # 16-bit
		valueBinary = pack('<h', valueLeft)
		self.outputFile.writeframes(valueBinary)
		valueRight = int(floor(self.valueRight / 5 * 32767)) # 16-bit
		valueBinary = pack('<h', valueRight)
		self.outputFile.writeframes(valueBinary)

class Sequencer:
	gate = 0                        # 0 or +5, float
	gateLength = 0                  # -5 to +5, float
	notes = []                      # Unlimited list of strings
	noteNumber = 0                  # 0 to unlimited, int
	noteTable = ['C-', 'C#', 'D-', 'D#', 'E-', 'F-', 'F#', 'G-', 'G#', 'A-', 'A#', 'B-']
	noteTime = 0                    # 0 to unlimited, float
	pitch = 0                       # 0 to +5, float
	semiquaverLength = 0            # 0 to unlimited, float
	temperament = '12e'             # '12e'
	tempo = 120                     # 0 to unlimited, float
	time = 0                        # 0 to self.getTrackLength(), float

	def __init__(self):
		self.setTempo(120)            # Default to 120BPM
		self.setGateLength(0)         # Default to half the note length

	def addNote(self, note):
		self.notes.append(note)

	def getGate(self):
		return self.gate

	def getPitch(self):
		return self.pitch

	def getTrackLength(self):
		return len(self.notes) * self.semiquaverLength

	def getTime(self):
		return self.time

	def incrementTime(self):
		increment = float(1) / float(44100)
		self.time = self.time + increment

		# Work out the current note
		noteNumber = int(self.time // self.semiquaverLength)

		if noteNumber > len(self.notes) - 1:
			noteNumber = len(self.notes) - 1

		if noteNumber > self.noteNumber:
			self.noteNumber = noteNumber
			self.noteTime = 0
		else:
			self.noteTime = self.noteTime + increment

		# Work out the current note's pitch
		note = self.notes[noteNumber]

		# Convert this pitch to a control voltage, 1v/oct
		if note[:3] == '...':
			self.gate = 0
			self.noteTime = 0
		elif self.temperament == '12e':
			gateLength = (self.gateLength + 5) / 10 * self.semiquaverLength

			if self.noteTime > gateLength:
				self.gate = 0
			else:
				self.gate = 5

			noteLetter = note[:2]
			noteOctave = int(note[2:])
			noteOctave = noteOctave - 1
			noteNumber = self.noteTable.index(noteLetter)
			self.pitch = noteOctave + (1 / 12 * noteNumber) # I should check if I need to make any of these explicitly floats on some setups.
		else:
			pass

		return increment

	def setGateLength(self, gateLength):
		self.gateLength = float(gateLength)

	def setTempo(self, tempo):
		self.tempo = float(tempo)
		crotchetLength = 60 / self.tempo
		semiquaverLength = crotchetLength / 4
		self.semiquaverLength = semiquaverLength
