# Surf, version 0.1, for Python 3.
# By ZoëB, 2012-04-10 to 2012-04-10.

# This is a software implementation of a basic modular synthesiser.
# Almost all values should be numbers between either -5 and +5,
# or 0 and +5.  Theoretically, it should one day be possible to connect
# this application to real modular hardware.

import sys
import wave

class NotationToCVConverter:
	temperament = '12e'             # '12e'
	noteTable = ['c', 'cs', 'd', 'ds', 'e', 'f', 'fs', 'g', 'gs', 'a', 'as', 'b']

	def __init__(self):
		pass

	def convert(self, note):
		if self.temperament == '12e':
			noteLetter = note[:-1]
			noteOctave = int(note[-1:])
			noteOctave = noteOctave - 1
			noteNumber = self.noteTable.index(noteLetter)
			return noteOctave + (1 / 12 * noteNumber)

class Oscillator:
	centOffset = 0                  # -5 to +5, float
	frequency = 0                   # 0 to +5, float
	octaveOffset = 0                # -5 to +5, int
	pulseWidth = 0                  # -5 to +5, float
	time = 0                        # 0 to unlimited, int

	def __init__(self):
		pass

	def getPulse(self):
		pass

	def getSine(self):
		pass

class Output:
	audioRefreshRate = 44100        # 0 to unlimited, int
	dataRefreshRate = 4410          # 0 to unlimited, int
	filename = 'surf.wav'
	time = 0                        # 0 to unlimited, int
	value = 0                       # -5 to +5, float

	def __del__(self):
		self.stop()

	def __init__(self):
		pass

	def setFilename(self, filename):
		self.filename = filename

	def setValue(self, value):
		self.value = value

	def start(self):
		self.outputFile = wave.open(self.filename, 'w')
		self.outputFile.setnchannels(2) # Stereo only
		self.outputFile.setsampwidth(2) # 16-bit only
		self.outputFile.setframerate(self.audioRefreshRate)

	def stop(self):
		self.outputFile.close()

	def write(self):
		value = self.value / 5 * 16384 # Still 16-bit only
		valueBinary = struct.pack('<hh', value)
		self.outputFile.writeframes(valueBinary)

class Sequencer:
	notes = []                      # Unlimited list of strings
	tempo = 120                     # 0 to unlimited, float
	time = 0                        # 0 to unlimited, int

	def __init__(self):
		pass

	def pushNote(self, note):
		self.notes.append(note)

	def setTempo(self, tempo):
		self.tempo = tempo
