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
		# Only make CD quality files
		self.outputFile = wave.open(self.filename, 'w')
		self.outputFile.setnchannels(2) # Stereo
		self.outputFile.setsampwidth(2) # 16-bit
		self.outputFile.setframerate(44100)

	def stop(self):
		self.outputFile.close()

	def write(self):
		value = self.value / 5 * 16384 # Still 16-bit only
		valueBinary = struct.pack('<hh', value)
		self.outputFile.writeframes(valueBinary)

# For now, there is only one channel, all notes are semiquavers, and there are no rests.
class Sequencer:
	notes = []                      # Unlimited list of strings
	semiquaverLength = 0            # 0 to unlimited, float
	tempo = 120                     # 0 to unlimited, float
	time = 0                        # 0 to self.getTrackLength(), float

	def __init__(self):
		self.setTempo(120)

	def addNote(self, note):
		self.notes.append(note)

	def getTrackLength(self):
		return len(self.notes) * self.semiquaverLength

	def getTime(self):
		return self.time

	def incrementTime(self):
		self.time = self.time + 1 / 44100

	def setTempo(self, tempo):
		self.tempo = tempo
		crotchetLength = 60 / self.tempo
		semiquaverLength = crotchetLength / 4
		self.semiquaverLength = semiquaverLength
