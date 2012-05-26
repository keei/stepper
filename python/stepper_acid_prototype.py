# Stepper Acid prototype application, for Python 3.

# This isn't a real Arduino emulator.  It just emulates millis(),
# and allows realtime testing of what the sequencer would output.

import curses
import math
import os
import stepper
import time

stepper.DEFAULT_NUMBER_OF_ROWS = 16
stepper.FILENAME = 'memory.sa'
stepper.MAX_NUMBER_OF_PATTERNS = 64
stepper.MAX_NUMBER_OF_ROWS = 16

clock = stepper.Clock()
sequencer = stepper.AcidSequencer()
slewLimiter = stepper.SlewLimiter()

try:
	sequencer.loadPattern(stepper.FILENAME)
except:
	pass

interface = curses.initscr()
ttySize = interface.getmaxyx()

if ttySize[0] < 24 or ttySize[1] < 80:
	curses.endwin()
	print('Please use a terminal with at least 80 by 24 characters.\n')
	exit()

interface.nodelay(True)
curses.noecho()
os.system('clear')

startTimeInSeconds = time.time()
lcdMode = 'tempo'
oddPulse = True # Think of it as starting at -1

def cursePrint(rowNumber, firstColumnNumber, string, invert = False):
	columnNumber = firstColumnNumber

	for char in string:
		if invert == True:
			interface.addch(rowNumber, columnNumber, char, curses.A_REVERSE)
		else:
			interface.addch(rowNumber, columnNumber, char)

		columnNumber = columnNumber + 1

def millis():
	return int((time.time() - startTimeInSeconds) * 1000)

while (True):
	# Updating values in real time
	timeInMilliseconds = millis()
	lastPulse = clock.getPulse()
	clock.setTime(millis())
	pulse = clock.getPulse()
	run = clock.getRun()

	# Count every other pulse, going from 96 PPQN to 48 PPQN
	if run == stepper.HIGH and lastPulse == stepper.LOW and pulse == stepper.HIGH:
		# In C, we can use a bitwise mutually-exclusive-or for this
		if oddPulse == True:
			oddPulse = False
		else:
			oddPulse = True

		if oddPulse == False:
			sequencer.incrementPulseCount()

	# Outputs for synthesisers
	slewLimiter.setPitch(sequencer.getPitchInTwelveBits(), sequencer.getSlideInTwelveBits(), millis())
	pitchInTwelveBits = slewLimiter.getPitchInTwelveBits()
	accentInTwelveBits = sequencer.getAccentInTwelveBits()
	gateInTwelveBits = sequencer.getGateInTwelveBits()

	# Outputs for LEDs, LCDs etc (internal components generally)
	clipboardFull = sequencer.getClipboardStatus()
	accent = sequencer.getAccentInSixtieths()
	gate = sequencer.getGateInSixtieths()
	# octave = sequencer.getOctave()
	pitch = sequencer.getPitchInSixtieths()
	semitone = sequencer.getSemitone()
	slide = sequencer.getSlideInSixtieths()

	# Output
	currentRowNumber = sequencer.getCurrentRowNumber()
	patternInSixtieths = sequencer.patternInSixtieths

	cursePrint(0, 0, 'XXX . Pattern select . Pattern length . Tempo   . Copy')
	cursePrint(1, 0, 'W E    R                T                Y         I  ')
	cursePrint(2, 0, '                                      9 Transpose  0  ')
	cursePrint(3, 0, '    .     .        .     .     .                     ')
	cursePrint(4, 0, ' . C#  . D#  .  . F#  . G#  . A#  .  .  .  .  .  .   ')
	cursePrint(5, 0, 'C-  S D-  D E- F-  G G-  H A-  J B- NT DN UP AC SL BK')
	cursePrint(6, 0, ' Z     X     C  V     B     N     M  ;  ,  .  \'  /  Q')
	cursePrint(7, 0, '                                                   FW')
	cursePrint(8, 0, '    . Run/stop 1                                    A')
	cursePrint(11, 0, '                                    Space bar to quit')

	cursePrint(12, 0, 'Pitch           ' + sequencer.convertTwelveBitsIntoChars(pitchInTwelveBits))
	cursePrint(13, 0, 'Accent          ' + sequencer.convertTwelveBitsIntoChars(accentInTwelveBits))
	cursePrint(14, 0, 'Gate            ' + sequencer.convertTwelveBitsIntoChars(gateInTwelveBits))

	# Print out the whole current pattern's rows
	cursePrint(0, 55, 'NTE SL GT AC')
	i = 1

	for row in patternInSixtieths:
		if i - 1 == currentRowNumber:
			cursePrint(i, 55, sequencer.convertPitchInSixtiethsIntoChars(row['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row['accent']), True)
		elif i - 1 < sequencer.numberOfRows:
			cursePrint(i, 55, sequencer.convertPitchInSixtiethsIntoChars(row['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row['accent']))
		else:
			cursePrint(i, 55, '... .. .. ..')

		i = i + 1

	# Print out the LCD area's settings
	if lcdMode == 'patternSelect':
		cursePrint(0, 0, sequencer.convertNumberIntoChars(sequencer.getCurrentPatternNumber()))
		cursePrint(0, 4, 'o')
	elif lcdMode == 'patternLength':
		cursePrint(0, 0, sequencer.convertNumberIntoChars(sequencer.getPatternLength()))
		cursePrint(0, 21, 'o')
	elif lcdMode == 'tempo':
		cursePrint(0, 0, sequencer.convertNumberIntoChars(clock.getTempo()))
		cursePrint(0, 38, 'o')

	if clipboardFull == True:
		cursePrint(0, 48, 'o')

	if run == stepper.HIGH:
		cursePrint(8, 4, 'o')

	# Print out the current row
	if semitone == 0:
		cursePrint(4, 1, 'o')
	elif semitone == 1:
		cursePrint(3, 4, 'o')
	elif semitone == 2:
		cursePrint(4, 7, 'o')
	elif semitone == 3:
		cursePrint(3, 10, 'o')
	elif semitone == 4:
		cursePrint(4, 13, 'o')
	elif semitone == 5:
		cursePrint(4, 16, 'o')
	elif semitone == 6:
		cursePrint(3, 19, 'o')
	elif semitone == 7:
		cursePrint(4, 22, 'o')
	elif semitone == 8:
		cursePrint(3, 25, 'o')
	elif semitone == 9:
		cursePrint(4, 28, 'o')
	elif semitone == 10:
		cursePrint(3, 31, 'o')
	elif semitone == 11:
		cursePrint(4, 34, 'o')

	if gate != 0:
		gateCharacter = 'o'
	else:
		gateCharacter = '.'

	if pitch < 24:
		octaveDownCharacter = 'o'
		octaveUpCharacter = '.'
	elif pitch > 35:
		octaveDownCharacter = '.'
		octaveUpCharacter = 'o'
	else:
		octaveDownCharacter = '.'
		octaveUpCharacter = '.'

	if accent != 0:
		accentCharacter = 'o'
	else:
		accentCharacter = '.'

	if slide == 60:
		slideCharacter = 'o'
	else:
		slideCharacter = '.'

	cursePrint(4, 37, gateCharacter)
	cursePrint(4, 40, octaveDownCharacter)
	cursePrint(4, 43, octaveUpCharacter)
	cursePrint(4, 46, accentCharacter)
	cursePrint(4, 49, slideCharacter)

	# Input
	try:
		key = interface.getkey()
	except:
		key = ''

	if key == ' ':
		curses.echo()
		curses.endwin()
		exit()

	if key == 'w':
		if lcdMode == 'patternSelect':
			sequencer.savePattern(stepper.FILENAME) # This is needed in case the user is going to a hitherto non-existent pattern, without saving (ie changing, which auto-saves) the current one first

			if run == stepper.HIGH:
				sequencer.decrementNextPatternNumber()
			else:
				sequencer.decrementCurrentPatternNumber()
		elif lcdMode == 'patternLength':
			sequencer.removeRow()
			sequencer.savePattern(stepper.FILENAME)
		elif lcdMode == 'tempo':
			clock.decrementTempo()

	if key == 'e':
		if lcdMode == 'patternSelect':
			sequencer.savePattern(stepper.FILENAME)

			if run == stepper.HIGH:
				sequencer.incrementNextPatternNumber()
			else:
				sequencer.incrementCurrentPatternNumber()
		elif lcdMode == 'patternLength':
			sequencer.addRow()
			sequencer.savePattern(stepper.FILENAME)
		elif lcdMode == 'tempo':
			clock.incrementTempo()

	if key == 'r':
		lcdMode = 'patternSelect'

	if key == 't':
		lcdMode = 'patternLength'

	if key == 'y':
		lcdMode = 'tempo'

	if key == 'i':
		if clipboardFull == True:
			sequencer.pastePattern()
			sequencer.savePattern(stepper.FILENAME)
		else:
			sequencer.copyPattern()

	if key == '9':
		sequencer.transposePatternDown()

	if key == '0':
		sequencer.transposePatternUp()

	if key == '1':
		if clock.getRunRequest() == stepper.HIGH:
			clock.setRunRequest(stepper.LOW)
			sequencer.resetPulseCount()
		else:
			clock.setRunRequest(stepper.HIGH)
			sequencer.setNextPatternNumber(sequencer.getCurrentPatternNumber())

	if key == 'z':
		if sequencer.getSemitone() == 0 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(0)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == 's':
		if sequencer.getSemitone() == 1 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(1)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == 'x':
		if sequencer.getSemitone() == 2 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(2)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == 'd':
		if sequencer.getSemitone() == 3 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(3)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == 'c':
		if sequencer.getSemitone() == 4 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(4)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == 'v':
		if sequencer.getSemitone() == 5 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(5)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == 'g':
		if sequencer.getSemitone() == 6 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(6)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == 'b':
		if sequencer.getSemitone() == 7 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(7)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == 'h':
		if sequencer.getSemitone() == 8 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(8)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == 'n':
		if sequencer.getSemitone() == 9 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(9)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == 'j':
		if sequencer.getSemitone() == 10 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(10)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == 'm':
		if sequencer.getSemitone() == 11 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(11)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == ';':
		if sequencer.getGateInSixtieths() == 0:
			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(35)
		else:
			sequencer.setGate(0)

		sequencer.savePattern(stepper.FILENAME)

	if key == ',':
		currentPitch = sequencer.getPitchInSixtieths()

		if currentPitch > 11:
			sequencer.setPitch(currentPitch - 12)

		sequencer.savePattern(stepper.FILENAME)

	if key == '.':
		currentPitch = sequencer.getPitchInSixtieths()

		if currentPitch < 49:
			sequencer.setPitch(currentPitch + 12)

		sequencer.savePattern(stepper.FILENAME)

	if key == '\'':
		if sequencer.getAccentInSixtieths() == 0:
			sequencer.setAccent(60)
		else:
			sequencer.setAccent(0)

		sequencer.savePattern(stepper.FILENAME)

	if key == '/':
		if sequencer.getSlideInSixtieths() == 60:
			sequencer.setSlide(0)

			if sequencer.getGateInSixtieths() == 60:
				sequencer.setGate(35)
		else:
			sequencer.setSlide(60)

			if sequencer.getGateInSixtieths() == 35:
				sequencer.setGate(60)

		sequencer.savePattern(stepper.FILENAME)

	if key == 'q':
		sequencer.decrementCurrentRowNumber()

	if key == 'a':
		sequencer.incrementCurrentRowNumber()
