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

def cursePrint(rowNumber, string):
	columnNumber = 0

	for char in string:
		interface.addch(rowNumber, columnNumber, char)
		columnNumber = columnNumber + 1

def millis():
	return int((time.time() - startTimeInSeconds) * 1000)

while (True):
	try:
		key = interface.getkey()
	except:
		key = ''

	if key == 'q':
		curses.echo()
		curses.endwin()
		exit()

	timeInMilliseconds = millis()
	timeInSeconds = timeInMilliseconds / 1000.0
	incrementLengthInSeconds = timeInSeconds - previousCycleTimeInSeconds
	sequencer.incrementTime(incrementLengthInSeconds)
	previousCycleTimeInSeconds = timeInSeconds

	pitch = sequencer.getPitch(0)
	cv1 = sequencer.getCV1(0)
	cv2 = sequencer.getCV2(0)
	gate = sequencer.getGate(0)

	currentEventRowNumber = sequencer.getCurrentEventRowNumber()
	patternLength = sequencer.getPatternLength()
	swing = sequencer.getSwing()

	for i in range(10):
		cursePrint(i, '                                                ')

	interface.move(0, 0)
	cursePrint(0, 'Time            ' + str(timeInMilliseconds))

	cursePrint(2, 'Pitch           ' + str(pitch))
	cursePrint(3, 'CV1             ' + str(cv1))
	cursePrint(4, 'CV2             ' + str(cv2))
	cursePrint(5, 'Gate            ' + str(gate))

	cursePrint(7, 'Event row       ' + str(currentEventRowNumber))
	cursePrint(8, 'Pattern length  ' + str(patternLength))
	cursePrint(9, 'Swing           ' + str(swing))
