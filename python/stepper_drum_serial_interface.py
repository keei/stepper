# Stepper Drum serial interface, for Python 3.

import curses
import glob
import os
import serial

interface = curses.initscr()
ttySize = interface.getmaxyx()
steppers = glob.glob('/dev/tty.usbmodem*') # Find Stepper automatically, regardless of which USB port it's on

if not steppers:
	curses.endwin()
	print('Please connect Stepper Drum to your computer.\n')
	exit()

try:
	ser = serial.Serial(steppers[0], 115200, timeout=0.1)
except serial.serialutil.SerialException:
	curses.endwin()
	print('Please connect Stepper Drum to your computer.\n')
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
patternNumber = 0
numberOfRows = 16
clipboardFull = 0
selectedInstrument = 0

pattern = []

for row in range(16):
	pattern.append({})
	pattern[row] = 0

while (True):
	try:
		state = ser.readline()
		state = state.decode()
	except serial.serialutil.SerialException:
		state = 'XXXXXX'

	if state[0:6] == 'GLOBAL' and len(state) == 32:
		clockRun = int(state[9:11], 16)
		clockTempo = int(state[13:15], 16)
		selectedInstrument = int(state[17:19], 16)
		patternNumber = int(state[21:23], 16)
		numberOfRows = int(state[25:27], 16)
		clipboardFull = int(state[29:31], 16)
	elif state[0:6] == 'ROWALL' and len(state) == 55:
		for row in range(16):
			pattern[row] = int(state[7 + (row * 3):9 + (row * 3)], 16)

	cursePrint(0, 0, 'XXX . Pattern select . Pattern length . Tempo   . Copy')
	cursePrint(1, 0, 'W E    R                T                Y         I  ')
	cursePrint(3, 0, '. . . . . . . .                                      ')
	cursePrint(4, 0, '1 2 3 4 5 6 7 8                   Instrument         ')
	cursePrint(5, 0, '                                                     ')
	cursePrint(6, 0, '. . . . . . . . . . . . . . . .                      ')
	cursePrint(7, 0, 'A S D F G H J K Z X C V B N M ,   Notes              ')
	cursePrint(8, 0, '    . Run/stop Q                                     ')
	cursePrint(11, 0, '                                    Space bar to quit')

	# Print out the whole current pattern's rows
	cursePrint(0, 55, '12345678')
	i = 1

	for row in pattern:
		if i - 1 < numberOfRows:
			cursePrint(i, 55, '00000000')

			for instrument in range (8):
				if row & (2 ** instrument):
					cursePrint(i, 55 + instrument, '1')
		else:
			cursePrint(i, 55, '........')

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
	cursePrint(3, selectedInstrument * 2, 'o')

	for row in range(16):
		if pattern[row] & (2 ** selectedInstrument):
			cursePrint(6, row * 2, 'o')

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

	if key == 'q':
		ser.write(b'\x00') # Run/stop

	if key == 'a':
		ser.write(b'\x0D') # Toggle note in 1st row

	if key == 's':
		ser.write(b'\x0E') # Toggle note in 2nd row

	if key == 'd':
		ser.write(b'\x0F') # Toggle note in 3rd row

	if key == 'f':
		ser.write(b'\x10') # Toggle note in 4th row

	if key == 'g':
		ser.write(b'\x11') # Toggle note in 5th row

	if key == 'h':
		ser.write(b'\x12') # Toggle note in 6th row

	if key == 'j':
		ser.write(b'\x13') # Toggle note in 7th row

	if key == 'k':
		ser.write(b'\x14') # Toggle note in 8th row

	if key == 'z':
		ser.write(b'\x15') # Toggle note in 9th row

	if key == 'x':
		ser.write(b'\x16') # Toggle note in 10th row

	if key == 'c':
		ser.write(b'\x17') # Toggle note in 11th row

	if key == 'v':
		ser.write(b'\x18') # Toggle note in 12th row

	if key == 'b':
		ser.write(b'\x19') # Toggle note in 13th row

	if key == 'n':
		ser.write(b'\x1A') # Toggle note in 14th row

	if key == 'm':
		ser.write(b'\x1B') # Toggle note in 15th row

	if key == ',':
		ser.write(b'\x1C') # Toggle note in 16th row

	if key == '1':
		ser.write(b'\x1D') # Select 1st instrument

	if key == '2':
		ser.write(b'\x1E') # Select 2nd instrument

	if key == '3':
		ser.write(b'\x1F') # Select 3rd instrument

	if key == '4':
		ser.write(b'\x20') # Select 4th instrument

	if key == '5':
		ser.write(b'\x21') # Select 5th instrument

	if key == '6':
		ser.write(b'\x22') # Select 6th instrument

	if key == '7':
		ser.write(b'\x23') # Select 7th instrument

	if key == '8':
		ser.write(b'\x24') # Select 8th instrument

	if key == 'R':
		ser.write(b'\xFF') # Factory reset
