# Tracker 4 prototype, for Python 3.
# By ZoeB.

import curses
import math
import os
import surf
import time

surf.DEFAULT_NUMBER_OF_ROWS = 16
surf.MAX_NUMBER_OF_PATTERNS = 64
surf.MAX_NUMBER_OF_ROWS = 16
surf.NUMBER_OF_CHANNELS = 4

sequencer = surf.Sequencer()

try:
	sequencer.loadPattern('memory.tracker4')
except:
	pass

previousCycleTimeInSeconds = 0

interface = curses.initscr()
interface.nodelay(True)
curses.noecho()
os.system('clear')
ttySize = interface.getmaxyx()

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
	try:
		key = interface.getkey()
	except:
		key = ''

	if key == ' ':
		curses.echo()
		curses.endwin()
		exit()

	if key == 'a':
		if lcdMode == 'patternSelect':
			sequencer.savePattern('memory.tracker4') # This is needed in case the user is going to a hitherto non-existent pattern, without saving (ie changing, which auto-saves) the current one first

			if sequencer.getPlayMode() == 1:
				sequencer.decrementNextPatternNumber()
			elif sequencer.getPlayMode() == 0:
				sequencer.decrementCurrentPatternNumber()
				sequencer.loadPattern('memory.tracker4')
		elif lcdMode == 'patternLength':
			sequencer.removeRow()
			sequencer.savePattern('memory.tracker4')
		elif lcdMode == 'tempo':
			sequencer.decrementTempo()

	if key == 's':
		if lcdMode == 'patternSelect':
			sequencer.savePattern('memory.tracker4')

			if sequencer.getPlayMode() == 1:
				sequencer.incrementNextPatternNumber()
			elif sequencer.getPlayMode() == 0:
				sequencer.incrementCurrentPatternNumber()
				sequencer.loadPattern('memory.tracker4')
		elif lcdMode == 'patternLength':
			sequencer.addRow()
			sequencer.savePattern('memory.tracker4')
		elif lcdMode == 'tempo':
			sequencer.incrementTempo()

	if key == 'd':
		lcdMode = 'patternSelect'

	if key == 'f':
		lcdMode = 'patternLength'

	if key == 'g':
		lcdMode = 'tempo'

	if key == 'h':
		if clipboardFull == True:
			sequencer.pastePattern()
			sequencer.savePattern('memory.tracker4')
		else:
			sequencer.copyPattern()

	if key == 'j':
		sequencer.transposePatternDown()

	if key == 'k':
		sequencer.transposePatternUp()

	if key == 'q':
		if sequencer.getSemitone() == 0 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(0)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern('memory.tracker4')

	if key == '2':
		if sequencer.getSemitone() == 1 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(1)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern('memory.tracker4')

	if key == 'w':
		if sequencer.getSemitone() == 2 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(2)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern('memory.tracker4')

	if key == '3':
		if sequencer.getSemitone() == 3 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(3)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern('memory.tracker4')

	if key == 'e':
		if sequencer.getSemitone() == 4 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(4)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern('memory.tracker4')

	if key == 'r':
		if sequencer.getSemitone() == 5 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(5)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern('memory.tracker4')

	if key == '5':
		if sequencer.getSemitone() == 6 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(6)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern('memory.tracker4')

	if key == 't':
		if sequencer.getSemitone() == 7 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(7)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern('memory.tracker4')

	if key == '6':
		if sequencer.getSemitone() == 8 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(8)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern('memory.tracker4')

	if key == 'y':
		if sequencer.getSemitone() == 9 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(9)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern('memory.tracker4')

	if key == '7':
		if sequencer.getSemitone() == 10 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(10)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern('memory.tracker4')

	if key == 'u':
		if sequencer.getSemitone() == 11 and sequencer.getGateInSixtieths() != 0:
			sequencer.setGate(0)
		else:
			sequencer.setSemitone(11)

			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)

		sequencer.incrementCurrentRowNumber()
		sequencer.savePattern('memory.tracker4')

	if key == 'i':
		if sequencer.getGateInSixtieths() == 0:
			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)
		else:
			sequencer.setGate(0)

		sequencer.savePattern('memory.tracker4')

	if key == 'o':
		currentPitch = sequencer.getPitchInSixtieths()

		if currentPitch > 11:
			sequencer.setPitch(currentPitch - 12)

		sequencer.savePattern('memory.tracker4')

	if key == 'p':
		currentPitch = sequencer.getPitchInSixtieths()

		if currentPitch < 49:
			sequencer.setPitch(currentPitch + 12)

		sequencer.savePattern('memory.tracker4')

	if key == '[':
		if sequencer.getCV1InSixtieths() == 0:
			sequencer.setCV1(60)
		else:
			sequencer.setCV1(0)

		sequencer.savePattern('memory.tracker4')

	if key == ']':
		if sequencer.getSlideInSixtieths() == 60:
			sequencer.setSlide(0)

			if sequencer.getGateInSixtieths() == 60:
				sequencer.setGate(30)
		else:
			sequencer.setSlide(60)

			if sequencer.getGateInSixtieths() == 30:
				sequencer.setGate(60)

		sequencer.savePattern('memory.tracker4')

	# if key == chr(curses.KEY_BACKSPACE):
	if key == '-':
		sequencer.decrementCurrentRowNumber()

	# if key == chr(curses.KEY_ENTER):
	if key == '=':
		sequencer.incrementCurrentRowNumber()

	timeInMilliseconds = millis()
	timeInSeconds = timeInMilliseconds / 1000.0
	incrementLengthInSeconds = timeInSeconds - previousCycleTimeInSeconds
	sequencer.incrementTime(incrementLengthInSeconds)
	iterationsThisSecond = iterationsThisSecond + 1

	if math.floor(timeInSeconds) != math.floor(previousCycleTimeInSeconds):
		iterationsPerSecond = iterationsThisSecond
		iterationsThisSecond = 0

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

	currentRowNumber = sequencer.getCurrentRowNumber()
	patternInSixtieths = sequencer.patternInSixtieths

	for i in range(14):
		cursePrint(i, 0, '                                                ')

	cursePrint(0, 0, 'Pattern: XXX  Length: XXX  Tempo: XXX  [Copy]')

	# Print out the whole current pattern's rows
	cursePrint(2, 0, 'NT SL GT AC')
	i = 3

	for row in patternInSixtieths:
		if i == ttySize[0]:
			break

		if i - 3 == currentRowNumber:
			cursePrint(i, 0, sequencer.convertSixtiethIntoChars(row[0]['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['cv1']), True)
		else:
			cursePrint(i, 0, sequencer.convertSixtiethIntoChars(row[0]['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['cv1']))

		i = i + 1

	for i in range(i, ttySize[0]):
		cursePrint(i, 0, '                      ') # In case a row's just been removed, or the pattern's just been changed

	# Print out the LCD area's settings
	cursePrint(0, 9, sequencer.convertNumberIntoChars(sequencer.getCurrentPatternNumber()))
	cursePrint(0, 22, sequencer.convertNumberIntoChars(sequencer.getPatternLength()))
	cursePrint(0, 34, sequencer.convertNumberIntoChars(sequencer.getTempo()))

	if clipboardFull == True:
		cursePrint(0, 39, '[Copy]', True)

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
