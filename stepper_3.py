# Arduino emulator, for Python 3.
# By ZoeB.

# This isn't a real Arduino emulator.  It just emulates millis(),
# and allows realtime testing of what the sequencer would output.

import curses
import os
import surf
import time

sequencer = surf.Sequencer()
sequencer.setTempo(120)
sequencer.setLoop(True)

pattern = open('2012.txt')

for eventRow in pattern:
	sequencer.addEventRow(eventRow)

previousCycleTimeInSeconds = 0

interface = curses.initscr()
interface.nodelay(True)
curses.noecho()
os.system('clear')

startTimeInSeconds = time.time()

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

	if key == 'q':
		pass

	if key == '2':
		pass

	if key == 'w':
		pass

	if key == '3':
		pass

	if key == 'e':
		pass

	if key == 'r':
		pass

	if key == '5':
		pass

	if key == 't':
		pass

	if key == '6':
		pass

	if key == 'y':
		pass

	if key == '7':
		pass

	if key == 'u':
		pass

	if key == 'i':
		pass

	if key == 'o':
		pass

	if key == 'p':
		pass

	if key == '[':
		pass

	if key == ']':
		if sequencer.getSlide() == True:
			sequencer.setSlide(False)
		else:
			sequencer.setSlide(True)

	# if key == chr(curses.KEY_BACKSPACE):
	if key == 'n':
		sequencer.decrementCurrentEventRowNumber()

	# if key == chr(curses.KEY_ENTER):
	if key == 'm':
		sequencer.incrementCurrentEventRowNumber()

	timeInMilliseconds = millis()
	timeInSeconds = timeInMilliseconds / 1000.0
	incrementLengthInSeconds = timeInSeconds - previousCycleTimeInSeconds
	sequencer.incrementTime(incrementLengthInSeconds)
	previousCycleTimeInSeconds = timeInSeconds

	pitch = sequencer.getPitch(0)
	cv1 = sequencer.getCV1(0)
	cv2 = sequencer.getCV2(0)
	gate = sequencer.getGate(0)

	playing = sequencer.getPlaying()
	currentEventRowNumber = sequencer.getCurrentEventRowNumber()
	patternLength = sequencer.getPatternLength()
	swing = sequencer.getSwing()

	pattern = sequencer.patterns[sequencer.currentPatternNumber]

	for i in range(14):
		cursePrint(i, 0, '                                                ')

	interface.move(0, 0)
	cursePrint(0, 0, 'Time            ' + str(timeInMilliseconds))

	cursePrint(2, 0, 'Pitch           ' + str(pitch))
	cursePrint(3, 0, 'CV1             ' + str(cv1))
	cursePrint(4, 0, 'CV2             ' + str(cv2))
	cursePrint(5, 0, 'Gate            ' + str(gate))

	cursePrint(7, 0, 'Playing         ' + str(playing))
	cursePrint(8, 0, 'Event row       ' + str(currentEventRowNumber))
	cursePrint(9, 0, 'Pattern length  ' + str(patternLength))
	cursePrint(10, 0, 'Swing           ' + str(swing))

	cursePrint(12, 0, 'Tab to toggle play/stop mode')
	cursePrint(13, 0, 'Space bar to quit')

	i = 0

	for eventRow in pattern:
		if eventRow[0]['slide'] == True:
			slideCharacter = 'S'
		else:
			slideCharacter = '.'

		if i == currentEventRowNumber:
			cursePrint(i, 36, eventRow[0]['pitch'] + ' ' + slideCharacter + ' ' + eventRow[0]['gate'] + ' ' + eventRow[0]['cv1'] + ' ' + eventRow[0]['cv2'], True)
		else:
			cursePrint(i, 36, eventRow[0]['pitch'] + ' ' + slideCharacter + ' ' + eventRow[0]['gate'] + ' ' + eventRow[0]['cv1'] + ' ' + eventRow[0]['cv2'])

		i = i + 1