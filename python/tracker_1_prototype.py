# Tracker 1 prototype application, for Python 3.

import curses
import math
import os
import stepper

stepper.DEFAULT_NUMBER_OF_ROWS = 16
stepper.FILENAME = 'tracker1.stp'
stepper.MAX_NUMBER_OF_PATTERNS = 128
stepper.MAX_NUMBER_OF_ROWS = 16
stepper.NUMBER_OF_CHANNELS = 4

sequencer = stepper.Sequencer()

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

curses.noecho()
os.system('clear')

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

	# Print out the header information
	cursePrint(0, 0, 'Pattern: XXX  Length: XXX  Tempo: XXX  Transpose  [Copy]       Space bar to quit')
	cursePrint(1, 0, '         W E          R T         Y U  9       0    I        Load/save automated')

	cursePrint(3, 0, '    NOTE      OCT SLD GAT CV1 CV2 CUR')
	cursePrint(4, 0, ' S D  G H J                        Q')
	cursePrint(5, 0, 'Z X CV B N M  , .  /  \';\\ [ ] - = OAP                               12345678')

	cursePrint(0, 9, sequencer.convertNumberIntoChars(sequencer.getCurrentPatternNumber()))
	cursePrint(0, 22, sequencer.convertNumberIntoChars(sequencer.getPatternLength()))
	cursePrint(0, 34, sequencer.convertNumberIntoChars(sequencer.getTempo()))

	if sequencer.getClipboardStatus() == True:
		cursePrint(0, 50, '[Copy]', True)

	# Print out the whole current pattern
	# CVs and gates
	for channel in range(stepper.NUMBER_OF_CHANNELS):
		channelOffset = channel * 17
		cursePrint(7, channelOffset, 'NTE SL GT CV CV')
		i = 8

		for row in patternInSixtieths:
			if i - 8 == currentRowNumber and channel == currentChannelNumber:
				cursePrint(i, channelOffset, sequencer.convertPitchInSixtiethsIntoChars(row[channel]['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['cv1']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['cv2']), True)
			elif i - 8 < sequencer.numberOfRows:
				cursePrint(i, channelOffset, sequencer.convertPitchInSixtiethsIntoChars(row[channel]['pitch']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['slide']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['cv1']) + ' ' + sequencer.convertSixtiethIntoChars(row[channel]['cv2']))
			else:
				cursePrint(i, channelOffset, '... .. .. .. ..')

			i = i + 1

	# Triggers
	channelOffset = stepper.NUMBER_OF_CHANNELS * 17
	cursePrint(7, channelOffset, 'TRIGGERS')
	i = 8

	for row in range(stepper.MAX_NUMBER_OF_ROWS):
		if i - 8 == currentRowNumber:
			cursePrint(i, channelOffset, sequencer.convertTriggerByteIntoChars(sequencer.triggerPattern[row]), True)
		else:
			cursePrint(i, channelOffset, sequencer.convertTriggerByteIntoChars(sequencer.triggerPattern[row]))

		i = i + 1

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
		sequencer.savePattern(stepper.FILENAME) # This is needed in case the user is going to a hitherto non-existent pattern, without saving (ie changing, which auto-saves) the current one first
		sequencer.decrementCurrentPatternNumber()
		sequencer.loadPattern(stepper.FILENAME)

	if key == 'e':
		sequencer.savePattern(stepper.FILENAME)
		sequencer.incrementCurrentPatternNumber()
		sequencer.loadPattern(stepper.FILENAME)

	if key == 'r':
		sequencer.removeRow()
		sequencer.savePattern(stepper.FILENAME)

	if key == 't':
		sequencer.addRow()
		sequencer.savePattern(stepper.FILENAME)

	if key == 'y':
		sequencer.decrementTempo()

	if key == 'u':
		sequencer.incrementTempo()

	if key == '9':
		sequencer.transposePatternDown()

	if key == '0':
		sequencer.transposePatternUp()

	if key == 'i':
		if sequencer.getClipboardStatus() == True:
			sequencer.pastePattern()
			sequencer.savePattern(stepper.FILENAME)
		else:
			sequencer.copyPattern()

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

	if key == '1':
		sequencer.toggleTrigger(1)

	if key == '2':
		sequencer.toggleTrigger(2)

	if key == '3':
		sequencer.toggleTrigger(3)

	if key == '4':
		sequencer.toggleTrigger(4)

	if key == '5':
		sequencer.toggleTrigger(5)

	if key == '6':
		sequencer.toggleTrigger(6)

	if key == '7':
		sequencer.toggleTrigger(7)

	if key == '8':
		sequencer.toggleTrigger(8)

	if key == ';':
		if sequencer.getGateInSixtieths() == 0:
			if sequencer.getSlideInSixtieths() == 60:
				sequencer.setGate(60)
			else:
				sequencer.setGate(30)
		else:
			sequencer.setGate(0)

		sequencer.savePattern(stepper.FILENAME)

	if key == '\'':
		gateInSixtieths = sequencer.getGateInSixtieths()

		if gateInSixtieths > 0:
			sequencer.setGate(gateInSixtieths - 1)

		sequencer.savePattern(stepper.FILENAME)

	if key == '\\':
		gateInSixtieths = sequencer.getGateInSixtieths()

		if gateInSixtieths < 60:
			sequencer.setGate(gateInSixtieths + 1)

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

	if key == '[':
		cv1InSixtieths = sequencer.getCV1InSixtieths()

		if cv1InSixtieths > 0:
			sequencer.setCV1(cv1InSixtieths - 1)

		sequencer.savePattern(stepper.FILENAME)

	if key == ']':
		cv1InSixtieths = sequencer.getCV1InSixtieths()

		if cv1InSixtieths < 60:
			sequencer.setCV1(cv1InSixtieths + 1)

		sequencer.savePattern(stepper.FILENAME)

	if key == '-':
		cv2InSixtieths = sequencer.getCV2InSixtieths()

		if cv2InSixtieths > 0:
			sequencer.setCV2(cv2InSixtieths - 1)

		sequencer.savePattern(stepper.FILENAME)

	if key == '=':
		cv2InSixtieths = sequencer.getCV2InSixtieths()

		if cv2InSixtieths < 60:
			sequencer.setCV2(cv2InSixtieths + 1)

		sequencer.savePattern(stepper.FILENAME)

	if key == 'q':
		sequencer.decrementCurrentRowNumber()

	if key == 'a':
		sequencer.incrementCurrentRowNumber()

	if key == 'o':
		sequencer.decrementCurrentChannelNumber()

	if key == 'p':
		sequencer.incrementCurrentChannelNumber()
