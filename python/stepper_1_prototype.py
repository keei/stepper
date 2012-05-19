# Stepper 1 prototype application, for Python 3.

# This isn't a real Arduino emulator.  It just emulates millis(),
# and allows realtime testing of what the sequencer would output.

import curses
import math
import os
import stepper
import time

stepper.DEFAULT_NUMBER_OF_ROWS = 16
stepper.MAX_NUMBER_OF_PATTERNS = 64
stepper.MAX_NUMBER_OF_ROWS = 16
stepper.NUMBER_OF_CHANNELS = 1

sequencer = stepper.Sequencer()
sequencer.slideCV1 = False # This won't have a DAC
sequencer.slideCV2 = False # This won't exist at all

try:
	sequencer.loadPattern('memory.stepper1')
except:
	pass

previousCycleTimeInMilliseconds = 0
previousCycleTimeInSeconds = 0.0

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
iterationsPerSecond = 0
iterationsThisSecond = 0
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
	timeInSeconds = timeInMilliseconds / 1000.0
	incrementLengthInMilliseconds = timeInMilliseconds - previousCycleTimeInMilliseconds
	incrementLengthInSeconds = timeInSeconds - previousCycleTimeInSeconds
	sequencer.incrementTime(incrementLengthInMilliseconds)
	iterationsThisSecond = iterationsThisSecond + 1

	if math.floor(timeInSeconds) != math.floor(previousCycleTimeInSeconds):
		iterationsPerSecond = iterationsThisSecond
		iterationsThisSecond = 0

	previousCycleTimeInMilliseconds = timeInMilliseconds
	previousCycleTimeInSeconds = timeInSeconds

	pitchInTwelveBits = sequencer.getPitchInTwelveBits(0)
	cv1InTwelveBits = sequencer.getCV1InTwelveBits(0)
	gateInTwelveBits = sequencer.getGateInTwelveBits(0)

	clipboardFull = sequencer.getClipboardStatus()
	cv1 = sequencer.getCV1InSixtieths()
	gate = sequencer.getGateInSixtieths()
	# octave = sequencer.getOctave()
	pitch = sequencer.getPitchInSixtieths()
	semitone = sequencer.getSemitone()
	slide = sequencer.getSlideInSixtieths()

	# Output
	currentRowNumber = sequencer.getCurrentRowNumber()
	patternInSixtieths = sequencer.patternInSixtieths

	for i in range(14):
		cursePrint(i, 0, '                                                ')

	interface.move(0, 0)
	cursePrint(0, 0, 'Time            ' + str(timeInMilliseconds))
	cursePrint(1, 0, 'Iterations/sec  ' + str(iterationsPerSecond))

	cursePrint(3, 0, 'Pitch           ' + sequencer.convertTwelveBitsIntoChars(pitchInTwelveBits))
	cursePrint(4, 0, 'CV1             ' + sequencer.convertTwelveBitsIntoChars(cv1InTwelveBits))
	cursePrint(5, 0, 'CV2             N/A')
	cursePrint(6, 0, 'Gate            ' + sequencer.convertTwelveBitsIntoChars(gateInTwelveBits))

	cursePrint(8, 0, 'XXX . Pattern select . Pattern length . Tempo   . Copy')
	cursePrint(9, 0, 'W E    R                T                Y         I  ')
	cursePrint(10, 0, '                                      9 Transpose  0  ')
	cursePrint(11, 0, '    .     .        .     .     .                     ')
	cursePrint(12, 0, ' . C#  . D#  .  . F#  . G#  . A#  .  .  .  .  .  .   ')
	cursePrint(13, 0, 'C-  S D-  D E- F-  G G-  H A-  J B- NT DN UP AC SL BK')
	cursePrint(14, 0, ' Z     X     C  V     B     N     M  ;  ,  .  \'  /  Q')
	cursePrint(15, 0, '                                                   FW')
	cursePrint(16, 0, '    . Pattern loop  1                               A')
	cursePrint(17, 0, '    . Song loop     2                                ')
	cursePrint(18, 0, '    . Song one-shot 3                                ')
	cursePrint(19, 0, '                                    Space bar to quit')

	# Print out the whole current pattern's rows
	cursePrint(0, 55, 'NTE SL GT AC')
	i = 1

	for row in patternInSixtieths:
		if i - 1 == currentRowNumber:
			cursePrint(i, 55, sequencer.convertPitchInSixtiethsIntoChars(row[0]['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['cv1']), True)
		else:
			cursePrint(i, 55, sequencer.convertPitchInSixtiethsIntoChars(row[0]['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['cv1']))

		i = i + 1

	# Print out the LCD area's settings
	if lcdMode == 'patternSelect':
		cursePrint(8, 0, sequencer.convertNumberIntoChars(sequencer.getCurrentPatternNumber()))
		cursePrint(8, 4, 'o')
	elif lcdMode == 'patternLength':
		cursePrint(8, 0, sequencer.convertNumberIntoChars(sequencer.getPatternLength()))
		cursePrint(8, 21, 'o')
	elif lcdMode == 'tempo':
		cursePrint(8, 0, sequencer.convertNumberIntoChars(sequencer.getTempo()))
		cursePrint(8, 38, 'o')

	if clipboardFull == True:
		cursePrint(8, 48, 'o')

	playMode = sequencer.getPlayMode()

	if playMode == 1:
		cursePrint(16, 4, 'o')
	elif playMode == 2:
		cursePrint(17, 4, 'o')
	elif playMode == 3:
		cursePrint(18, 4, 'o')

	# Print out the current row
	if semitone == 0:
		cursePrint(12, 1, 'o')
	elif semitone == 1:
		cursePrint(11, 4, 'o')
	elif semitone == 2:
		cursePrint(12, 7, 'o')
	elif semitone == 3:
		cursePrint(11, 10, 'o')
	elif semitone == 4:
		cursePrint(12, 13, 'o')
	elif semitone == 5:
		cursePrint(12, 16, 'o')
	elif semitone == 6:
		cursePrint(11, 19, 'o')
	elif semitone == 7:
		cursePrint(12, 22, 'o')
	elif semitone == 8:
		cursePrint(11, 25, 'o')
	elif semitone == 9:
		cursePrint(12, 28, 'o')
	elif semitone == 10:
		cursePrint(11, 31, 'o')
	elif semitone == 11:
		cursePrint(12, 34, 'o')

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

	cursePrint(12, 37, gateCharacter)
	cursePrint(12, 40, octaveDownCharacter)
	cursePrint(12, 43, octaveUpCharacter)
	cursePrint(12, 46, cv1Character)
	cursePrint(12, 49, slideCharacter)

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
			sequencer.savePattern('memory.stepper1') # This is needed in case the user is going to a hitherto non-existent pattern, without saving (ie changing, which auto-saves) the current one first

			if sequencer.getPlayMode() == 1:
				sequencer.decrementNextPatternNumber()
			elif sequencer.getPlayMode() == 0:
				sequencer.decrementCurrentPatternNumber()
				sequencer.loadPattern('memory.stepper1')
		elif lcdMode == 'patternLength':
			sequencer.removeRow()
			sequencer.savePattern('memory.stepper1')
		elif lcdMode == 'tempo':
			sequencer.decrementTempo()

	if key == 'e':
		if lcdMode == 'patternSelect':
			sequencer.savePattern('memory.stepper1')

			if sequencer.getPlayMode() == 1:
				sequencer.incrementNextPatternNumber()
			elif sequencer.getPlayMode() == 0:
				sequencer.incrementCurrentPatternNumber()
				sequencer.loadPattern('memory.stepper1')
		elif lcdMode == 'patternLength':
			sequencer.addRow()
			sequencer.savePattern('memory.stepper1')
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
			sequencer.savePattern('memory.stepper1')
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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

	if key == ';':
		if sequencer.getGateInSixtieths() == 0:
			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)
		else:
			sequencer.setGate(0)

		sequencer.savePattern('memory.stepper1')

	if key == ',':
		currentPitch = sequencer.getPitchInSixtieths()

		if currentPitch > 11:
			sequencer.setPitch(currentPitch - 12)

		sequencer.savePattern('memory.stepper1')

	if key == '.':
		currentPitch = sequencer.getPitchInSixtieths()

		if currentPitch < 49:
			sequencer.setPitch(currentPitch + 12)

		sequencer.savePattern('memory.stepper1')

	if key == '\'':
		if sequencer.getCV1InSixtieths() == 0:
			sequencer.setCV1(60)
		else:
			sequencer.setCV1(0)

		sequencer.savePattern('memory.stepper1')

	if key == '/':
		if sequencer.getSlideInSixtieths() == 60:
			sequencer.setSlide(0)

			if sequencer.getGateInSixtieths() == 60:
				sequencer.setGate(30)
		else:
			sequencer.setSlide(60)

			if sequencer.getGateInSixtieths() == 30:
				sequencer.setGate(60)

		sequencer.savePattern('memory.stepper1')

	if key == 'q':
		sequencer.decrementCurrentRowNumber()

	if key == 'a':
		sequencer.incrementCurrentRowNumber()

