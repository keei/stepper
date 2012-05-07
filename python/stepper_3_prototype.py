# Stepper 3 prototype, for Python 3.
# By ZoeB.

# This isn't a real Arduino emulator.  It just emulates millis(),
# and allows realtime testing of what the sequencer would output.

import curses
import math
import os
import surf
import time

sequencer = surf.Sequencer()
# sequencer.loadSong('2012.xml')
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
			sequencer.decrementCurrentPatternNumber()
		elif lcdMode == 'patternLength':
			sequencer.removeRow()
		elif lcdMode == 'tempo':
			sequencer.decrementTempo()

	if key == 's':
		if lcdMode == 'patternSelect':
			sequencer.incrementCurrentPatternNumber()
		elif lcdMode == 'patternLength':
			sequencer.addRow()
		elif lcdMode == 'tempo':
			sequencer.incrementTempo()

	if key == 'd':
		lcdMode = 'patternSelect'

	if key == 'f':
		lcdMode = 'patternLength'

	if key == 'g':
		lcdMode = 'tempo'

	if key == 'q':
		if sequencer.getSemitone() == 0 and sequencer.getPitchInSixtiethsAndDots() != 61:
			sequencer.setPitch(61)
		else:
			sequencer.setSemitone(0)

		sequencer.incrementCurrentRowNumber()

	if key == '2':
		if sequencer.getSemitone() == 1:
			sequencer.setPitch(61)
		else:
			sequencer.setSemitone(1)

		sequencer.incrementCurrentRowNumber()

	if key == 'w':
		if sequencer.getSemitone() == 2:
			sequencer.setPitch(61)
		else:
			sequencer.setSemitone(2)

		sequencer.incrementCurrentRowNumber()

	if key == '3':
		if sequencer.getSemitone() == 3:
			sequencer.setPitch(61)
		else:
			sequencer.setSemitone(3)

		sequencer.incrementCurrentRowNumber()

	if key == 'e':
		if sequencer.getSemitone() == 4:
			sequencer.setPitch(61)
		else:
			sequencer.setSemitone(4)

		sequencer.incrementCurrentRowNumber()

	if key == 'r':
		if sequencer.getSemitone() == 5:
			sequencer.setPitch(61)
		else:
			sequencer.setSemitone(5)

		sequencer.incrementCurrentRowNumber()

	if key == '5':
		if sequencer.getSemitone() == 6:
			sequencer.setPitch(61)
		else:
			sequencer.setSemitone(6)

		sequencer.incrementCurrentRowNumber()

	if key == 't':
		if sequencer.getSemitone() == 7:
			sequencer.setPitch(61)
		else:
			sequencer.setSemitone(7)

		sequencer.incrementCurrentRowNumber()

	if key == '6':
		if sequencer.getSemitone() == 8:
			sequencer.setPitch(61)
		else:
			sequencer.setSemitone(8)

		sequencer.incrementCurrentRowNumber()

	if key == 'y':
		if sequencer.getSemitone() == 9:
			sequencer.setPitch(61)
		else:
			sequencer.setSemitone(9)

		sequencer.incrementCurrentRowNumber()

	if key == '7':
		if sequencer.getSemitone() == 10:
			sequencer.setPitch(61)
		else:
			sequencer.setSemitone(10)

		sequencer.incrementCurrentRowNumber()

	if key == 'u':
		if sequencer.getSemitone() == 11:
			sequencer.setPitch(61)
		else:
			sequencer.setSemitone(11)

		sequencer.incrementCurrentRowNumber()

	if key == 'i':
		if sequencer.getGateInSixtieths() == 0:
			sequencer.setGate(61)
		else:
			sequencer.setGate(0)

	if key == 'o':
		if sequencer.getOctave() == 1:
			sequencer.setOctave(0)
		else:
			sequencer.setOctave(1)

	if key == 'p':
		if sequencer.getOctave() == 1:
			sequencer.setOctave(2)
		else:
			sequencer.setOctave(1)

	if key == '[':
		if sequencer.getCV1InSixtieths() == 0:
			sequencer.setCV1(60)
		else:
			sequencer.setCV1(0)

	if key == ']':
		if sequencer.getSlide() == True:
			sequencer.setSlide(False)
		else:
			sequencer.setSlide(True)

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

	pitchOutput = sequencer.getPitchOutput(0)
	cv1Output = sequencer.getCV1Output(0)
	gateOutput = sequencer.getGateOutput(0)

	cv1 = sequencer.getCV1InSixtieths()
	gate = sequencer.getGateInSixtiethsAndDots()
	octave = sequencer.getOctave()
	pitchName = sequencer.getPitchInSixtiethsAndDots()
	semitone = sequencer.getSemitone()
	slide = sequencer.getSlide()

	currentRowNumber = sequencer.getCurrentRowNumber()
	patternInSixtiethsAndDots = sequencer.patternsInSixtiethsAndDots[sequencer.currentPatternNumber]
	patternInSixtieths = sequencer.patternsInSixtieths[sequencer.currentPatternNumber]

	for i in range(14):
		cursePrint(i, 0, '                                                ')

	interface.move(0, 0)
	cursePrint(0, 0, 'Time            ' + str(timeInMilliseconds))
	cursePrint(1, 0, 'Iterations/sec  ' + str(iterationsPerSecond))

	cursePrint(3, 0, 'Pitch           ' + str(pitchOutput))
	cursePrint(4, 0, 'CV1             ' + str(cv1Output))
	cursePrint(5, 0, 'CV2             N/A')
	cursePrint(6, 0, 'Gate            ' + str(gateOutput))

	cursePrint(8, 0, 'XXX . Pattern select . Pattern length . Tempo         ')
	cursePrint(9, 0, 'A S    D                F                G            ')
	cursePrint(10, 0, '    .     .        .     .     .                     ')
	cursePrint(11, 0, ' . C#  . D#  .  . F#  . G#  . A#  .  .  .  .  .  .   ')
	cursePrint(12, 0, 'C-  2 D-  3 E- F-  5 G-  6 A-  7 B- NT DN UP AC SL BK')
	cursePrint(13, 0, ' Q     W     E  R     T     Y     U  I  O  P  [  ]  -')
	cursePrint(14, 0, '                                                   FW')
	cursePrint(15, 0, '                                                    =')

	cursePrint(17, 0, 'Tab to toggle play/stop mode')
	cursePrint(18, 0, 'Space bar to quit')

	# Print out the whole current pattern's events
	i = 0

	for event in patternInSixtiethsAndDots:
		if event[0]['slide'] == True:
			slideCharacter = 'S'
		else:
			slideCharacter = '.'

		if i == currentRowNumber:
			cursePrint(i, 55, sequencer.convertSixtiethIntoChars(event[0]['pitch']) + ' ' + slideCharacter + ' ' + sequencer.convertSixtiethIntoChars(event[0]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(event[0]['cv1']), True)
		else:
			cursePrint(i, 55, sequencer.convertSixtiethIntoChars(event[0]['pitch']) + ' ' + slideCharacter + ' ' + sequencer.convertSixtiethIntoChars(event[0]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(event[0]['cv1']))

		i = i + 1

	for i in range(i, ttySize[0]):
		cursePrint(i, 55, '                      ') # In case a row's just been removed, or the pattern's just been changed
	i = 0

	for event in patternInSixtieths:
		if event[0]['slide'] == True:
			slideCharacter = 'S'
		else:
			slideCharacter = '.'

		if i == currentRowNumber:
			cursePrint(i, 67, sequencer.convertSixtiethIntoChars(event[0]['pitch']) + ' ' + slideCharacter + ' ' + sequencer.convertSixtiethIntoChars(event[0]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(event[0]['cv1']), True)
		else:
			cursePrint(i, 67, sequencer.convertSixtiethIntoChars(event[0]['pitch']) + ' ' + slideCharacter + ' ' + sequencer.convertSixtiethIntoChars(event[0]['gate']) + ' ' + sequencer.convertSixtiethIntoChars(event[0]['cv1']))

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

	# Print out the current event
	if semitone == 0 and pitchName != 61:
		cursePrint(11, 1, 'o')
	elif semitone == 1:
		cursePrint(10, 4, 'o')
	elif semitone == 2:
		cursePrint(11, 7, 'o')
	elif semitone == 3:
		cursePrint(10, 10, 'o')
	elif semitone == 4:
		cursePrint(11, 13, 'o')
	elif semitone == 5:
		cursePrint(11, 16, 'o')
	elif semitone == 6:
		cursePrint(10, 19, 'o')
	elif semitone == 7:
		cursePrint(11, 22, 'o')
	elif semitone == 8:
		cursePrint(10, 25, 'o')
	elif semitone == 9:
		cursePrint(11, 28, 'o')
	elif semitone == 10:
		cursePrint(10, 31, 'o')
	elif semitone == 11:
		cursePrint(11, 34, 'o')

	if gate != 0 and (gate != 61 or pitchName != 61):
		gateCharacter = 'o'
	else:
		gateCharacter = '.'

	if octave == 0:
		octaveDownCharacter = 'o'
		octaveUpCharacter = '.'
	elif octave == 2:
		octaveDownCharacter = '.'
		octaveUpCharacter = 'o'
	else:
		octaveDownCharacter = '.'
		octaveUpCharacter = '.'

	if cv1 != 0:
		cv1Character = 'o'
	else:
		cv1Character = '.'

	if slide == True:
		slideCharacter = 'o'
	else:
		slideCharacter = '.'

	cursePrint(11, 37, gateCharacter)
	cursePrint(11, 40, octaveDownCharacter)
	cursePrint(11, 43, octaveUpCharacter)
	cursePrint(11, 46, cv1Character)
	cursePrint(11, 49, slideCharacter)
