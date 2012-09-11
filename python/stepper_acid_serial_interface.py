# Stepper Acid serial interface, for Python 3.

import curses
import glob
import os
import serial

interface = curses.initscr()
ttySize = interface.getmaxyx()
steppers = glob.glob('/dev/tty.usbmodem*') # Find Stepper automatically, regardless of which USB port it's on

if not steppers:
	curses.endwin()
	print('Please connect Stepper Acid to your computer.\n')
	exit()

try:
	ser = serial.Serial(steppers[0], 115200, timeout=0.1)
except serial.serialutil.SerialException:
	curses.endwin()
	print('Please connect Stepper Acid to your computer.\n')
	exit()

if ttySize[0] < 24 or ttySize[1] < 80:
	curses.endwin()
	print('Please use a terminal with at least 80 by 24 characters.\n')
	exit()

interface.nodelay(True)
curses.noecho()
os.system('clear')

lcdMode = 'tempo'

def convertNumberIntoChars(number):
	"""Convert a number into three characters, suitable for display on an LCD."""
	number = int(number)
	number = '%03d' % number
	return number

def convertPitchInSixtiethsIntoChars(sixtieth):
	"""Convert a number between 0 and 60 into three characters depicting the note in a more human readable form, suitable for display on a screen with a fixed width font."""
	semitone = sixtieth % 12
	octave = int(sixtieth / 12)

	semitoneNames = ['C-', 'C#', 'D-', 'D#', 'E-', 'F-', 'F#', 'G-', 'G#', 'A-', 'A#', 'B-']

	semitone = semitoneNames[semitone]
	return semitone + str(octave)

def cursePrint(rowNumber, firstColumnNumber, string, invert = False):
	columnNumber = firstColumnNumber

	for char in string:
		if invert == True:
			interface.addch(rowNumber, columnNumber, char, curses.A_REVERSE)
		else:
			interface.addch(rowNumber, columnNumber, char)

		columnNumber = columnNumber + 1

# Defaults
clockRun = 0
clockTempo = 120
rowNumber = 0
patternNumber = 0
numberOfRows = 16
clipboardFull = 0

pattern = []

for row in range(16):
	pattern.append({})
	pattern[row]['pitch'] = 24
	pattern[row]['slide'] = '..'
	pattern[row]['gate'] = '..'
	pattern[row]['accent'] = '..'

while (True):
	try:
		state = ser.readline()
		state = state.decode()
	except serial.serialutil.SerialException:
		state = 'XXXXXX'

	if state[0:6] == 'GLOBAL' and len(state) == 32:
		clockRun = int(state[9:11], 16)
		clockTempo = int(state[13:15], 16)
		rowNumber = int(state[17:19], 16)
		patternNumber = int(state[21:23], 16)
		numberOfRows = int(state[25:27], 16)
		clipboardFull = int(state[29:31], 16)
	elif state[0:4] == 'ROW ' and len(state) == 24:
		row = int(state[4:6], 16)
		pattern[row]['pitch'] = int(state[9:11], 16)

		if int(state[13:15], 16) == 1:
			pattern[row]['slide'] = 'SL'
		else:
			pattern[row]['slide'] = '..'

		if int(state[17:19], 16) == 1:
			pattern[row]['gate'] = 'GT'
		else:
			pattern[row]['gate'] = '..'

		if int(state[21:23], 16) == 1:
			pattern[row]['accent'] = 'AC'
		else:
			pattern[row]['accent'] = '..'

	cursePrint(0, 0, 'XXX . Pattern select . Pattern length . Tempo   . Copy')
	cursePrint(1, 0, 'W E    R                T                Y         I  ')
	cursePrint(2, 0, '                                      9 Transpose  0  ')
	cursePrint(3, 0, '    .     .        .     .     .                     ')
	cursePrint(4, 0, ' . C#  . D#  .  . F#  . G#  . A#  .  .  .  .  .  .   ')
	cursePrint(5, 0, 'C-  S D-  D E- F-  G G-  H A-  J B- NT DN UP AC SL BK')
	cursePrint(6, 0, ' Z     X     C  V     B     N     M  ;  ,  .  \'  /  Q')
	cursePrint(7, 0, '                                                   FW')
	cursePrint(8, 0, '    . Run/stop 1                                    A')
	cursePrint(11, 0, '                                    Space bar to quit')

	# Print out the whole current pattern's rows
	cursePrint(0, 55, 'NTE SL GT AC')
	i = 1

	for row in pattern:
		if i - 1 == rowNumber:
			cursePrint(i, 55, convertPitchInSixtiethsIntoChars(row['pitch']) + ' ' + row['slide'] + ' ' + row['gate'] + ' ' + row['accent'], True)
		elif i - 1 < numberOfRows:
			cursePrint(i, 55, convertPitchInSixtiethsIntoChars(row['pitch']) + ' ' + row['slide'] + ' ' + row['gate'] + ' ' + row['accent'])
		else:
			cursePrint(i, 55, '... .. .. ..')

		i = i + 1

	# Print out the LCD area's settings
	if lcdMode == 'patternSelect':
		cursePrint(0, 0, convertNumberIntoChars(patternNumber + 1))
		cursePrint(0, 4, 'o')
	elif lcdMode == 'patternLength':
		cursePrint(0, 0, convertNumberIntoChars(numberOfRows))
		cursePrint(0, 21, 'o')
	elif lcdMode == 'tempo':
		cursePrint(0, 0, convertNumberIntoChars(clockTempo))
		cursePrint(0, 38, 'o')

	if clipboardFull != 0:
		cursePrint(0, 48, 'o')

	if clockRun != 0:
		cursePrint(8, 4, 'o')

	# Turn on the appropriate LEDs
	if pattern[rowNumber]['pitch'] % 12 == 0:
		cursePrint(4, 1, 'o')
	elif pattern[rowNumber]['pitch'] % 12 == 1:
		cursePrint(3, 4, 'o')
	elif pattern[rowNumber]['pitch'] % 12 == 2:
		cursePrint(4, 7, 'o')
	elif pattern[rowNumber]['pitch'] % 12 == 3:
		cursePrint(3, 10, 'o')
	elif pattern[rowNumber]['pitch'] % 12 == 4:
		cursePrint(4, 13, 'o')
	elif pattern[rowNumber]['pitch'] % 12 == 5:
		cursePrint(4, 16, 'o')
	elif pattern[rowNumber]['pitch'] % 12 == 6:
		cursePrint(3, 19, 'o')
	elif pattern[rowNumber]['pitch'] % 12 == 7:
		cursePrint(4, 22, 'o')
	elif pattern[rowNumber]['pitch'] % 12 == 8:
		cursePrint(3, 25, 'o')
	elif pattern[rowNumber]['pitch'] % 12 == 9:
		cursePrint(4, 28, 'o')
	elif pattern[rowNumber]['pitch'] % 12 == 10:
		cursePrint(3, 31, 'o')
	elif pattern[rowNumber]['pitch'] % 12 == 11:
		cursePrint(4, 34, 'o')

	if pattern[rowNumber]['gate'] != 0:
		gateCharacter = 'o'
	else:
		gateCharacter = '.'

	if pattern[rowNumber]['pitch'] < 24:
		octaveDownCharacter = 'o'
		octaveUpCharacter = '.'
	elif pattern[rowNumber]['pitch'] > 35:
		octaveDownCharacter = '.'
		octaveUpCharacter = 'o'
	else:
		octaveDownCharacter = '.'
		octaveUpCharacter = '.'

	if pattern[rowNumber]['accent'] != 0:
		accentCharacter = 'o'
	else:
		accentCharacter = '.'

	if pattern[rowNumber]['slide'] == 60:
		slideCharacter = 'o'
	else:
		slideCharacter = '.'

	cursePrint(4, 37, gateCharacter)
	cursePrint(4, 40, octaveDownCharacter)
	cursePrint(4, 43, octaveUpCharacter)
	cursePrint(4, 46, accentCharacter)
	cursePrint(4, 49, slideCharacter)

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
			ser.write(b'\x05') # Decrement pattern number
		elif lcdMode == 'patternLength':
			ser.write(b'\x07') # Decrement number of rows (shorten pattern)
		elif lcdMode == 'tempo':
			ser.write(b'\x01') # Decrement tempo

	if key == 'e':
		if lcdMode == 'patternSelect':
			ser.write(b'\x06') # Increment pattern number
		elif lcdMode == 'patternLength':
			ser.write(b'\x08') # Increment number of rows (lengthen pattern)
		elif lcdMode == 'tempo':
			ser.write(b'\x02') # Increment tempo

	if key == 'r':
		lcdMode = 'patternSelect'

	if key == 't':
		lcdMode = 'patternLength'

	if key == 'y':
		lcdMode = 'tempo'

	if key == 'i':
		if clipboardFull != 0:
			ser.write(b'\x0A') # Paste pattern
		else:
			ser.write(b'\x09') # Copy pattern

	if key == '9':
		ser.write(b'\x0B') # Transpose pattern down a semitone

	if key == '0':
		ser.write(b'\x0C') # Transpose pattern up a semitone

	if key == '1':
		ser.write(b'\x00') # Run/stop

	if key == 'z':
		ser.write(b'\x0D') # Toggle note C

	if key == 's':
		ser.write(b'\x0E') # Toggle note C#

	if key == 'x':
		ser.write(b'\x0F') # Toggle note D

	if key == 'd':
		ser.write(b'\x10') # Toggle note D#

	if key == 'c':
		ser.write(b'\x11') # Toggle note E

	if key == 'v':
		ser.write(b'\x12') # Toggle note F

	if key == 'g':
		ser.write(b'\x13') # Toggle note F#

	if key == 'b':
		ser.write(b'\x14') # Toggle note G

	if key == 'h':
		ser.write(b'\x15') # Toggle note G#

	if key == 'n':
		ser.write(b'\x16') # Toggle note A

	if key == 'j':
		ser.write(b'\x17') # Toggle note A#

	if key == 'm':
		ser.write(b'\x18') # Toggle note B

	if key == ';':
		ser.write(b'\x1C') # Toggle gate

	if key == ',':
		ser.write(b'\x19') # Transpose note down an octave

	if key == '.':
		ser.write(b'\x1A') # Transpose note up an octave

	if key == '\'':
		ser.write(b'\x1D') # Toggle accent

	if key == '/':
		ser.write(b'\x1B') # Toggle slide

	if key == 'q':
		ser.write(b'\x03') # Decrement row number (move cursor back)

	if key == 'a':
		ser.write(b'\x04') # Increment row number (move cursor forwards)

	if key == 'R':
		ser.write(b'\xFF') # Factory reset
