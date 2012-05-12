# Tracker 4 prototype, for Python 3.
# By ZoeB.

import curses
import math
import os
import surf

surf.DEFAULT_NUMBER_OF_ROWS = 16
surf.MAX_NUMBER_OF_PATTERNS = 64
surf.MAX_NUMBER_OF_ROWS = 16
surf.NUMBER_OF_CHANNELS = 4

sequencer = surf.Sequencer()

try:
	sequencer.loadPattern('memory.tracker4')
except:
	pass

interface = curses.initscr()
curses.noecho()
os.system('clear')
ttySize = interface.getmaxyx()

def cursePrint(rowNumber, firstColumnNumber, string, invert = False):
	columnNumber = firstColumnNumber

	for char in string:
		if invert == True:
			interface.addch(rowNumber, columnNumber, char, curses.A_REVERSE)
		else:
			interface.addch(rowNumber, columnNumber, char)

		columnNumber = columnNumber + 1

while (True):
	# Output
	currentRowNumber = sequencer.getCurrentRowNumber()
	currentChannelNumber = sequencer.getCurrentChannelNumber()
	patternInSixtieths = sequencer.patternInSixtieths

	cursePrint(0, 0, 'Pattern: XXX  Length: XXX  Tempo: XXX  [Copy]')
	cursePrint(1, 0, '         A S          D F         G H    I   ')

	cursePrint(0, 9, sequencer.convertNumberIntoChars(sequencer.getCurrentPatternNumber()))
	cursePrint(0, 22, sequencer.convertNumberIntoChars(sequencer.getPatternLength()))
	cursePrint(0, 34, sequencer.convertNumberIntoChars(sequencer.getTempo()))

	if sequencer.getClipboardStatus() == True:
		cursePrint(0, 39, '[Copy]', True)

	# Print out the whole current pattern's rows
	for channel in range(surf.NUMBER_OF_CHANNELS):
		channelOffset = channel * 14
		cursePrint(3, channelOffset, 'NTE SL GT AC')
		i = 4

		for row in patternInSixtieths:
			if i == ttySize[0]:
				break

			if i - 4 == currentRowNumber and channel == currentChannelNumber:
				cursePrint(i, channelOffset, sequencer.convertPitchInSixtiethsIntoChars(row[channel]['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['cv1']), True)
			else:
				cursePrint(i, channelOffset, sequencer.convertPitchInSixtiethsIntoChars(row[channel]['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['cv1']))

			i = i + 1

		for i in range(i, ttySize[0]):
			cursePrint(i, channelOffset, '              ') # In case a row's just been removed, or the pattern's just been changed

	# Input
	try:
		key = interface.getkey()
	except:
		key = ''

	if key == ' ':
		curses.echo()
		curses.endwin()
		exit()

	if key == 'a':
		sequencer.savePattern('memory.tracker4') # This is needed in case the user is going to a hitherto non-existent pattern, without saving (ie changing, which auto-saves) the current one first
		sequencer.decrementCurrentPatternNumber()
		sequencer.loadPattern('memory.tracker4')

	if key == 's':
		sequencer.savePattern('memory.tracker4')
		sequencer.incrementCurrentPatternNumber()
		sequencer.loadPattern('memory.tracker4')

	if key == 'd':
		sequencer.removeRow()
		sequencer.savePattern('memory.tracker4')

	if key == 'f':
		sequencer.addRow()
		sequencer.savePattern('memory.tracker4')

	if key == 'g':
		sequencer.decrementTempo()

	if key == 'h':
		sequencer.incrementTempo()

	if key == 'i':
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

