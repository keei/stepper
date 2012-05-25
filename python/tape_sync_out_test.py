import stepper
import struct
import wave

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

		audioLeft = int(self.audioLeftInBipolarVolts / 5 * 32767) # 16-bit
		audioBinary = struct.pack('<h', audioLeft)
		self.buffer.append(audioBinary)
		audioRight = int(self.audioRightInBipolarVolts / 5 * 32767) # 16-bit
		audioBinary = struct.pack('<h', audioRight)
		self.buffer.append(audioBinary)

for bpm in (80, 120):
	bpmString = '%d' % bpm
	output = Output()
	output.setFilename('tape_sync_out_test_' + bpmString + 'bpm.wav')

	sequencer = stepper.Sequencer()
	sequencer.setTempo(bpm)

	# In my infinite wisdom, I made Stepper no longer work with increments that aren't integral multiples of a microsecond, so we'll have to increment time 1 microsecond at a time.  This will make the recording everso slightly the wrong speed.
	for sample in range(44100 * 10): # 10 second test; 44100 samples per second
		# Start playing after 2 seconds
		if sample == 2 * 44100:
			sequencer.setPlayMode(1)

		# Stop playing after 8 seconds
		if sample == 8 * 44100:
			sequencer.setPlayMode(0)

		sequencer.incrementTime(23) # There are roughly 23 microseconds in each 44.1kHz-lasting sample
		signal = sequencer.getTapeSyncTriggerOutputInTwelveBits()
		signal = signal / 4095.0 * 5.0

		output.setAudio(signal)
		output.write()
