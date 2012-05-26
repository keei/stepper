# Stepper Drum prototype application, for Python 3.

# This isn't a real Arduino emulator.  It just emulates millis(),
# and allows realtime testing of what the sequencer would output.

import curses
import math
import os
import stepper
import time

stepper.DEFAULT_NUMBER_OF_ROWS = 16
stepper.FILENAME = 'memory.sd'
stepper.MAX_NUMBER_OF_PATTERNS = 64
stepper.MAX_NUMBER_OF_ROWS = 16

clock = stepper.Clock()
sequencer = stepper.DrumSequencer()

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
	channel0 = sequencer.getTriggerInTwelveBits(0)
	channel1 = sequencer.getTriggerInTwelveBits(1)
	channel2 = sequencer.getTriggerInTwelveBits(2)
	channel3 = sequencer.getTriggerInTwelveBits(3)
	channel4 = sequencer.getTriggerInTwelveBits(4)
	channel5 = sequencer.getTriggerInTwelveBits(5)
	channel6 = sequencer.getTriggerInTwelveBits(6)
	channel7 = sequencer.getTriggerInTwelveBits(7)

	# Outputs for LEDs, LCDs etc (internal components generally)
	clipboardFull = sequencer.getClipboardStatus()

	# Output
	currentRowNumber = sequencer.getCurrentRowNumber()
	pattern = sequencer.pattern

	cursePrint(0, 0, 'XXX . Pattern select . Pattern length . Tempo   . Copy')
	cursePrint(1, 0, 'W E    R                T                Y         I  ')
	cursePrint(3, 0, '1 2 3 4 5 6 7 8')
	cursePrint(4, 0, 'Z X C V B N M ,')
	cursePrint(5, 0, 'Back     Q')
	cursePrint(6, 0, 'Forward  A')
	cursePrint(8, 0, '    . Run/stop 1')
	cursePrint(9, 0, '                                    Space bar to quit')

	cursePrint(12, 0, 'Channel 1       ' + sequencer.convertTwelveBitsIntoChars(channel0))
	cursePrint(13, 0, 'Channel 2       ' + sequencer.convertTwelveBitsIntoChars(channel1))
	cursePrint(14, 0, 'Channel 3       ' + sequencer.convertTwelveBitsIntoChars(channel2))
	cursePrint(15, 0, 'Channel 4       ' + sequencer.convertTwelveBitsIntoChars(channel3))
	cursePrint(16, 0, 'Channel 5       ' + sequencer.convertTwelveBitsIntoChars(channel4))
	cursePrint(17, 0, 'Channel 6       ' + sequencer.convertTwelveBitsIntoChars(channel5))
	cursePrint(18, 0, 'Channel 7       ' + sequencer.convertTwelveBitsIntoChars(channel6))
	cursePrint(19, 0, 'Channel 8       ' + sequencer.convertTwelveBitsIntoChars(channel7))

	# Print out the whole current pattern's rows
	cursePrint(0, 55, '12345678')
	i = 1

	for row in pattern:
		if i - 1 == currentRowNumber:
			cursePrint(i, 55, sequencer.convertTriggerByteIntoChars(row), True)
		elif i - 1 < sequencer.numberOfRows:
			cursePrint(i, 55, sequencer.convertTriggerByteIntoChars(row))
		else:
			cursePrint(i, 55, '........')

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

	if key == '1':
		if clock.getRunRequest() == stepper.HIGH:
			clock.setRunRequest(stepper.LOW)
			sequencer.resetPulseCount()
		else:
			clock.setRunRequest(stepper.HIGH)
			sequencer.setNextPatternNumber(sequencer.getCurrentPatternNumber())

	if key == 'z':
		sequencer.toggleTrigger(0)
		sequencer.savePattern(stepper.FILENAME)

	if key == 'x':
		sequencer.toggleTrigger(1)
		sequencer.savePattern(stepper.FILENAME)

	if key == 'c':
		sequencer.toggleTrigger(2)
		sequencer.savePattern(stepper.FILENAME)

	if key == 'v':
		sequencer.toggleTrigger(3)
		sequencer.savePattern(stepper.FILENAME)

	if key == 'b':
		sequencer.toggleTrigger(4)
		sequencer.savePattern(stepper.FILENAME)

	if key == 'n':
		sequencer.toggleTrigger(5)
		sequencer.savePattern(stepper.FILENAME)

	if key == 'm':
		sequencer.toggleTrigger(6)
		sequencer.savePattern(stepper.FILENAME)

	if key == ',':
		sequencer.toggleTrigger(7)
		sequencer.savePattern(stepper.FILENAME)

	if key == 'q':
		sequencer.decrementCurrentRowNumber()

	if key == 'a':
		sequencer.incrementCurrentRowNumber()
