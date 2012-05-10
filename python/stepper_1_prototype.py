# Stepper 1 prototype, for Python 3.
# By ZoeB.

# This isn't a real Arduino emulator.  It just emulates millis(),
# and allows realtime testing of what the sequencer would output.

import curses
import math
import os
import surf
import time

surf.DEFAULT_NUMBER_OF_ROWS = 16
surf.MAX_NUMBER_OF_PATTERNS = 64
surf.MAX_NUMBER_OF_ROWS = 64
surf.NUMBER_OF_CHANNELS = 1

sequencer = surf.Sequencer()
sequencer.slideCV1 = False # This won't have a DAC
sequencer.slideCV2 = False # This won't exist at all

try:
	sequencer.loadPattern('memory.stepper1')
except:
	pass

sequencer.setLoop(True)

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

	if key == '	':
		if sequencer.getPlaying() == True:
			sequencer.setPlaying(False)
		else:
			sequencer.setPlaying(True)

	if key == 'a':
		if lcdMode == 'patternSelect':
			sequencer.savePattern('memory.stepper1') # This is needed in case the user is going to a hitherto non-existent pattern, without saving (ie changing, which auto-saves) the current one first
			sequencer.decrementCurrentPatternNumber()
			sequencer.loadPattern('memory.stepper1')
		elif lcdMode == 'patternLength':
			sequencer.removeRow()
			sequencer.savePattern('memory.stepper1')
		elif lcdMode == 'tempo':
			sequencer.decrementTempo()

	if key == 's':
		if lcdMode == 'patternSelect':
			sequencer.savePattern('memory.stepper1')
			sequencer.incrementCurrentPatternNumber()
			sequencer.loadPattern('memory.stepper1')
		elif lcdMode == 'patternLength':
			sequencer.addRow()
			sequencer.savePattern('memory.stepper1')
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
			sequencer.savePattern('memory.stepper1')
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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

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
		sequencer.savePattern('memory.stepper1')

	if key == 'i':
		if sequencer.getGateInSixtieths() == 0:
			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)
		else:
			sequencer.setGate(0)

		sequencer.savePattern('memory.stepper1')

	if key == 'o':
		currentPitch = sequencer.getPitchInSixtieths()

		if currentPitch > 11:
			sequencer.setPitch(currentPitch - 12)

		sequencer.savePattern('memory.stepper1')

	if key == 'p':
		currentPitch = sequencer.getPitchInSixtieths()

		if currentPitch < 49:
			sequencer.setPitch(currentPitch + 12)

		sequencer.savePattern('memory.stepper1')

	if key == '[':
		if sequencer.getCV1InSixtieths() == 0:
			sequencer.setCV1(60)
		else:
			sequencer.setCV1(0)

		sequencer.savePattern('memory.stepper1')

	if key == ']':
		if sequencer.getSlideInSixtieths() == 60:
			sequencer.setSlide(0)
		else:
			sequencer.setSlide(60)

			if sequencer.getGateInSixtieths() == 30:
				sequencer.setGate(60)

		sequencer.savePattern('memory.stepper1')

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

	interface.move(0, 0)
	cursePrint(0, 0, 'Time            ' + str(timeInMilliseconds))
	cursePrint(1, 0, 'Iterations/sec  ' + str(iterationsPerSecond))

	cursePrint(3, 0, 'Pitch           ' + sequencer.convertTwelveBitsIntoChars(pitchInTwelveBits))
	cursePrint(4, 0, 'CV1             ' + sequencer.convertTwelveBitsIntoChars(cv1InTwelveBits))
	cursePrint(5, 0, 'CV2             N/A')
	cursePrint(6, 0, 'Gate            ' + sequencer.convertTwelveBitsIntoChars(gateInTwelveBits))

	cursePrint(8, 0, 'XXX . Pattern select . Pattern length . Tempo   . Copy')
	cursePrint(9, 0, 'A S    D                F                G         H  ')
	cursePrint(10, 0, '                                      J Transpose  K  ')
	cursePrint(11, 0, '    .     .        .     .     .                     ')
	cursePrint(12, 0, ' . C#  . D#  .  . F#  . G#  . A#  .  .  .  .  .  .   ')
	cursePrint(13, 0, 'C-  2 D-  3 E- F-  5 G-  6 A-  7 B- NT DN UP AC SL BK')
	cursePrint(14, 0, ' Q     W     E  R     T     Y     U  I  O  P  [  ]  -')
	cursePrint(15, 0, '                                                   FW')
	cursePrint(16, 0, '    . Pattern loop  Z                               =')
	cursePrint(17, 0, '    . Song loop     X                                ')
	cursePrint(18, 0, '    . Song one-shot C                                ')
	cursePrint(19, 0, '                                    Space bar to quit')

	# Print out the whole current pattern's rows
	cursePrint(0, 55, 'NT SL GT AC')
	i = 1

	for row in patternInSixtieths:
		if i == ttySize[0]:
			break

		if i - 1 == currentRowNumber:
			cursePrint(i, 55, sequencer.convertSixtiethIntoChars(row[0]['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['cv1']), True)
		else:
			cursePrint(i, 55, sequencer.convertSixtiethIntoChars(row[0]['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row[0]['cv1']))

		i = i + 1

	for i in range(i, ttySize[0]):
		cursePrint(i, 55, '                      ') # In case a row's just been removed, or the pattern's just been changed

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
