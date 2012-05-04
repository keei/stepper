# Arduino emulator, for Python 3.
# By ZoeB.

# This isn't a real Arduino emulator.  It just emulates millis(),
# and allows realtime testing of what the sequencer would output.

import curses
import math
import os
import surf
import time

sequencer = surf.Sequencer()
sequencer.loadSong('2012.xml')
sequencer.setLoop(True)

previousCycleTimeInSeconds = 0

interface = curses.initscr()
interface.nodelay(True)
curses.noecho()
os.system('clear')

startTimeInSeconds = time.time()
iterationsPerSecond = 0
iterationsThisSecond = 0

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
		sequencer.setSemitone('C-')

	if key == '2':
		sequencer.setSemitone('C#')
		pass

	if key == 'w':
		sequencer.setSemitone('D-')
		pass

	if key == '3':
		sequencer.setSemitone('D#')
		pass

	if key == 'e':
		sequencer.setSemitone('E-')
		pass

	if key == 'r':
		sequencer.setSemitone('F-')
		pass

	if key == '5':
		sequencer.setSemitone('F#')
		pass

	if key == 't':
		sequencer.setSemitone('G-')
		pass

	if key == '6':
		sequencer.setSemitone('G#')
		pass

	if key == 'y':
		sequencer.setSemitone('A-')
		pass

	if key == '7':
		sequencer.setSemitone('A#')
		pass

	if key == 'u':
		sequencer.setSemitone('B-')
		pass

	if key == 'i':
		sequencer.setSemitone('C-')
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
		sequencer.decrementCurrentRowNumber()

	# if key == chr(curses.KEY_ENTER):
	if key == 'm':
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

	pitch = sequencer.getPitch(0)
	cv1 = sequencer.getCV1(0)
	cv2 = sequencer.getCV2(0)
	gate = sequencer.getGate(0)

	pitchName = sequencer.getPitchName()
	octave = sequencer.getOctave()
	semitone = sequencer.getSemitone()
	slide = sequencer.getSlide()

	playing = sequencer.getPlaying()
	currentRowNumber = sequencer.getCurrentRowNumber()
	patternLength = sequencer.getPatternLength()
	swing = sequencer.getSwing()

	pattern = sequencer.patterns[sequencer.currentPatternNumber]

	for i in range(14):
		cursePrint(i, 0, '                                                ')

	interface.move(0, 0)
	cursePrint(0, 0, 'Time            ' + str(timeInMilliseconds))
	cursePrint(1, 0, 'Iterations/sec  ' + str(iterationsPerSecond))

	cursePrint(3, 0, 'Pitch           ' + str(pitch))
	cursePrint(4, 0, 'CV1             ' + str(cv1))
	cursePrint(5, 0, 'CV2             ' + str(cv2))
	cursePrint(6, 0, 'Gate            ' + str(gate))

	cursePrint(8, 0, 'Playing         ' + str(playing))
	cursePrint(9, 0, 'Current row     ' + str(currentRowNumber))
	cursePrint(10, 0, 'Pattern length  ' + str(patternLength))
	cursePrint(11, 0, 'Swing           ' + str(swing))

	cursePrint(13, 0, 'Tab to toggle play/stop mode')
	cursePrint(14, 0, 'Space bar to quit')

	# Print out the whole current pattern's events
	i = 0

	for event in pattern:
		if event[0]['slide'] == True:
			slideCharacter = 'S'
		else:
			slideCharacter = '.'

		if i == currentRowNumber:
			cursePrint(i, 36, event[0]['pitch'] + ' ' + slideCharacter + ' ' + event[0]['gate'] + ' ' + event[0]['cv1'] + ' ' + event[0]['cv2'], True)
		else:
			cursePrint(i, 36, event[0]['pitch'] + ' ' + slideCharacter + ' ' + event[0]['gate'] + ' ' + event[0]['cv1'] + ' ' + event[0]['cv2'])

		i = i + 1

	# Print out the current event
	i = i + 2

	if slide == True:
		slideCharacter = 'S'
	else:
		slideCharacter = '.'

	cursePrint(i, 36, pitchName + ' ' + slideCharacter)
	i = i + 1
	cursePrint(i, 36, semitone + ' ' + octave + ' (redundant)')
