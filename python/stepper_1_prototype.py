# Stepper 1 prototype application, for Python 3.

# This isn't a real Arduino emulator.  It just emulates millis(),
# and allows realtime testing of what the sequencer would output.

import curses
import math
import os
import stepper
import time

stepper.DEFAULT_NUMBER_OF_ROWS = 16
stepper.FILENAME = 'stepper1.stp'
stepper.MAX_NUMBER_OF_PATTERNS = 64
stepper.MAX_NUMBER_OF_ROWS = 16
stepper.NUMBER_OF_CHANNELS = 1

sequencer = stepper.Sequencer()
sequencer.slideCV1 = False # This won't have a DAC
sequencer.slideCV2 = False # This won't exist at all

try:
	sequencer.loadPattern(stepper.FILENAME)
except:
	pass

previousCycleTimeInMilliseconds = 0

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
	incrementLengthInMilliseconds = timeInMilliseconds - previousCycleTimeInMilliseconds
	sequencer.incrementTime(incrementLengthInMilliseconds)
	previousCycleTimeInMilliseconds = timeInMilliseconds

	# Outputs for synthesisers
	pitchInTwelveBits = sequencer.getPitchInTwelveBits(0)
	cv1InTwelveBits = sequencer.getCV1InTwelveBits(0)
	gateInTwelveBits = sequencer.getGateInTwelveBits(0)
	syncGateOutputInTwelveBits = sequencer.getSyncGateOutputInTwelveBits()
	syncTriggerOutputInTwelveBits = sequencer.getSyncTriggerOutputInTwelveBits()

	# Outputs for LEDs, LCDs etc (internal components generally)
	clipboardFull = sequencer.getClipboardStatus()
	cv1 = sequencer.getCV1InSixtieths()
	gate = sequencer.getGateInSixtieths()
	# octave = sequencer.getOctave()
	pitch = sequencer.getPitchInSixtieths()
	semitone = sequencer.getSemitone()
	slide = sequencer.getSlideInSixtieths()

	# Outputs for debugging
	absoluteTime = sequencer.getAbsoluteTime()
	playTime = sequencer.getPlayTime()

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
	cursePrint(8, 0, '    . Pattern loop  1                               A')
	cursePrint(9, 0, '    . Song loop     2                                ')
	cursePrint(10, 0, '    . Song one-shot 3                                ')
	cursePrint(11, 0, '                                    Space bar to quit')

	cursePrint(12, 0, 'Pitch           ' + sequencer.convertTwelveBitsIntoChars(pitchInTwelveBits))
	cursePrint(13, 0, 'CV1             ' + sequencer.convertTwelveBitsIntoChars(cv1InTwelveBits))
	cursePrint(14, 0, 'CV2             N/A')
	cursePrint(15, 0, 'Gate            ' + sequencer.convertTwelveBitsIntoChars(gateInTwelveBits))
	cursePrint(16, 0, 'Sync24 run/stop ' + sequencer.convertTwelveBitsIntoChars(syncGateOutputInTwelveBits) + ' O')
	cursePrint(17, 0, 'Sync24 clock    ' + sequencer.convertTwelveBitsIntoChars(syncTriggerOutputInTwelveBits) + ' P')

	cursePrint(19, 0, 'Absolute time   ' + sequencer.convertTwelveBitsIntoChars(absoluteTime))
	cursePrint(20, 0, 'Play time       ' + sequencer.convertTwelveBitsIntoChars(playTime))

	# Print out the whole current pattern's rows
	cursePrint(0, 55, 'NTE SL GT AC')
	i = 1

	for row in patternInSixtieths:
		if i - 1 == currentRowNumber:
			cursePrint(i, 55, sequencer.convertPitchInSixtiethsIntoChars(row[0]['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['cv1']), True)
		elif i - 1 < sequencer.numberOfRows:
			cursePrint(i, 55, sequencer.convertPitchInSixtiethsIntoChars(row[0]['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['cv1']))
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
		cursePrint(0, 0, sequencer.convertNumberIntoChars(sequencer.getTempo()))
		cursePrint(0, 38, 'o')

	if clipboardFull == True:
		cursePrint(0, 48, 'o')

	playMode = sequencer.getPlayMode()

	if playMode == 1:
		cursePrint(8, 4, 'o')
	elif playMode == 2:
		cursePrint(9, 4, 'o')
	elif playMode == 3:
		cursePrint(10, 4, 'o')

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

	if cv1 != 0:
		cv1Character = 'o'
	else:
		cv1Character = '.'

	if slide == 60:
		slideCharacter = 'o'
	else:
		slideCharacter = '.'

	cursePrint(4, 37, gateCharacter)
	cursePrint(4, 40, octaveDownCharacter)
	cursePrint(4, 43, octaveUpCharacter)
	cursePrint(4, 46, cv1Character)
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

			if sequencer.getPlayMode() == 1:
				sequencer.decrementNextPatternNumber()
			elif sequencer.getPlayMode() == 0:
				sequencer.decrementCurrentPatternNumber()
				sequencer.loadPattern(stepper.FILENAME)
		elif lcdMode == 'patternLength':
			sequencer.removeRow()
			sequencer.savePattern(stepper.FILENAME)
		elif lcdMode == 'tempo':
			sequencer.decrementTempo()

	if key == 'e':
		if lcdMode == 'patternSelect':
			sequencer.savePattern(stepper.FILENAME)

			if sequencer.getPlayMode() == 1:
				sequencer.incrementNextPatternNumber()
			elif sequencer.getPlayMode() == 0:
				sequencer.incrementCurrentPatternNumber()
				sequencer.loadPattern(stepper.FILENAME)
		elif lcdMode == 'patternLength':
			sequencer.addRow()
			sequencer.savePattern(stepper.FILENAME)
		elif lcdMode == 'tempo':
			sequencer.incrementTempo()

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
		if sequencer.getPlayMode() == 1:
			sequencer.setPlayMode(0)
		else:
			sequencer.setPlayMode(1)

	if key == '2':
		if sequencer.getPlayMode() == 2:
			sequencer.setPlayMode(0)
		else:
			sequencer.setPlayMode(2)

	if key == '3':
		if sequencer.getPlayMode() == 3:
			sequencer.setPlayMode(0)
		else:
			sequencer.setPlayMode(3)

	if key == 'z':
		if sequencer.getSemitone() == 0 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(0)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

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
				sequencer.setGate(30)

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
				sequencer.setGate(30)

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
				sequencer.setGate(30)

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
				sequencer.setGate(30)

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
				sequencer.setGate(30)

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
				sequencer.setGate(30)

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
				sequencer.setGate(30)

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
				sequencer.setGate(30)

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
				sequencer.setGate(30)

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
				sequencer.setGate(30)

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
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern(stepper.FILENAME)

	if key == ';':
		if sequencer.getGateInSixtieths() == 0:
			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)
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
		if sequencer.getCV1InSixtieths() == 0:
			sequencer.setCV1(60)
		else:
			sequencer.setCV1(0)

		sequencer.savePattern(stepper.FILENAME)

	if key == '/':
		if sequencer.getSlideInSixtieths() == 60:
			sequencer.setSlide(0)

			if sequencer.getGateInSixtieths() == 60:
				sequencer.setGate(30)
		else:
			sequencer.setSlide(60)

			if sequencer.getGateInSixtieths() == 30:
				sequencer.setGate(60)

		sequencer.savePattern(stepper.FILENAME)

	if key == 'q':
		sequencer.decrementCurrentRowNumber()

	if key == 'a':
		sequencer.incrementCurrentRowNumber()

	if key == 'o':
		sequencer.setSyncGate(stepper.HIGH)
	else:
		sequencer.setSyncGate(stepper.LOW)

	if key == 'p':
		sequencer.setSyncTrigger(stepper.HIGH)
	else:
		sequencer.setSyncTrigger(stepper.LOW)
