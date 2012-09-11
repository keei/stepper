/*
 *  Stepper Drum: a drum machine with trigger outputs.
 *  By Zoe Blade and Nina Richards.
 */

#include "Arduino.h"
#include "EEPROM.h"

/*
 *  Hardware constants
 */

#define DIGITAL_PIN_CLOCK_PULSE 2
#define DIGITAL_PIN_RUN_STOP 3
#define DIGITAL_PIN_CLOCK_SOURCE 4 /* Switch: LOW = internal, HIGH = external */
#define DIGITAL_PIN_FIRST_INSTRUMENT 5
#define DIGITAL_PIN_INTERNAL_LED 13 /* Using an Arduino Uno, this is standard */

#define INTERRUPT_CLOCK_PULSE 0

#define VIRGIN_MEMORY 255 /* As per http://arduino.cc/en/Reference/EEPROMRead */

/*
 *  Clock constants
 */

#define FROM_TEMPO_TO_MILLISECONDS 2500 /* 60 seconds per minute; 60 / BPM = quarter note length in seconds; 60,000 / BPM = quarter note length in milliseconds; quarter note length in milliseconds / 24 = clock pulse length in milliseconds; 60,000 / 24 = 2500; 2500 / BPM = pulse length in milliseconds */

/*
 *  Sequencer constants
 */

#define MAX_NUMBER_OF_PATTERNS 60 /* We only have 1k of EEPROM to play with */
#define MAX_NUMBER_OF_ROWS 16
#define SEQUENCER_PPSN 6 /* 24 PPQN = 6 PPSN */

/* Other note attributes */
#define OFF 0
#define ON 1

/*
 *  Main constants
 */

/* Input */
#define FIRST_CYCLE -2
#define NO_INPUT -1
#define RUN_STOP 0
#define DECREMENT_TEMPO 1
#define INCREMENT_TEMPO 2
#define DECREMENT_ROW_NUMBER 3
#define INCREMENT_ROW_NUMBER 4
#define DECREMENT_PATTERN_NUMBER 5
#define INCREMENT_PATTERN_NUMBER 6
#define DECREMENT_NUMBER_OF_ROWS 7
#define INCREMENT_NUMBER_OF_ROWS 8
#define COPY_PATTERN 9
#define PASTE_PATTERN 10
#define TOGGLE_NOTE_IN_ROW_01 13
#define TOGGLE_NOTE_IN_ROW_02 14
#define TOGGLE_NOTE_IN_ROW_03 15
#define TOGGLE_NOTE_IN_ROW_04 16
#define TOGGLE_NOTE_IN_ROW_05 17
#define TOGGLE_NOTE_IN_ROW_06 18
#define TOGGLE_NOTE_IN_ROW_07 19
#define TOGGLE_NOTE_IN_ROW_08 20
#define TOGGLE_NOTE_IN_ROW_09 21
#define TOGGLE_NOTE_IN_ROW_10 22
#define TOGGLE_NOTE_IN_ROW_11 23
#define TOGGLE_NOTE_IN_ROW_12 24
#define TOGGLE_NOTE_IN_ROW_13 25
#define TOGGLE_NOTE_IN_ROW_14 26
#define TOGGLE_NOTE_IN_ROW_15 27
#define TOGGLE_NOTE_IN_ROW_16 28
#define SELECT_INSTRUMENT_1 29
#define SELECT_INSTRUMENT_2 30
#define SELECT_INSTRUMENT_3 31
#define SELECT_INSTRUMENT_4 32
#define SELECT_INSTRUMENT_5 33
#define SELECT_INSTRUMENT_6 34
#define SELECT_INSTRUMENT_7 35
#define SELECT_INSTRUMENT_8 36
#define FACTORY_RESET 255

/*
 *  Universal, disposable variables
 *  These can be used and overwritten at any time by anything.  Be careful!
 */

unsigned char row = 0;
unsigned char item = 0;

/*
 *  Main variables
 */

unsigned char oddPulse = 1; /* Think of it as starting at -1, getting ready to increment to 0 in the first iteration */

/* Output */
char *output = "GLOBAL RSxxTMxxINxxPNxxPLxxCFxx\nROWALL xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx xx\nFOOTER\n\n";
char *hexDigit = "xx"; /* Converted to ASCII */

/* Input */
signed int input = FIRST_CYCLE;

/*
 *  Clock variables
 */

unsigned long clockLastPulse = LOW; /* The clock pulse state during the last iteration of the main code loop */
unsigned long clockLastTime = 0; /* When the last pulse started, in milliseconds */
unsigned long clockPulseCount = 0; /* The number of pulses that have happened so far overall. */
unsigned long clockPulseLength = 21; /* The amount of time between one pulse start and the next, in milliseconds.  Calculatd as FROM_TEMPO_TO_MILLISECONDS / clockTempo. */
unsigned char clockRun = LOW; /* Whether or not we're running */
unsigned char clockTempo = 120; /* In BPM */
unsigned char clockTempoRequest = 120; /* In BPM */
unsigned long clockTimeAbsolute = 0; /* The current overall time, in milliseconds */
unsigned long clockTimeAtRunStart = 0; /* The overall time when when the sequencer started running, in milliseconds */
unsigned long clockTimeRunning = 0; /* The current time since the sequencer started running, in milliseconds */

/*
 *  Sequencer variables
 */

unsigned char clipboard[MAX_NUMBER_OF_ROWS];
unsigned char clipboardFull = LOW;
unsigned char clipboardNumberOfRows = MAX_NUMBER_OF_ROWS;
unsigned char patternNumber = 0;
unsigned char patternNumberRequest = 0;
unsigned char numberOfRows = MAX_NUMBER_OF_ROWS;
unsigned char pattern[MAX_NUMBER_OF_ROWS];
unsigned char rowNumber = 0;
unsigned char selectedInstrument = 0;
unsigned short sequencerPulseCount = 0; /* The number of pulses that have happened so far in this pattern. */

/*
 *  Custom functions
 */

void loadPattern()
{
	numberOfRows = EEPROM.read((MAX_NUMBER_OF_ROWS + 1) * patternNumber);

	for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
		pattern[row] = EEPROM.read(((MAX_NUMBER_OF_ROWS + 1) * patternNumber) + 1 + row);
	}

	/* Ignore obvious errors, as in virgin EEPROM addresses */
	if (numberOfRows < 1 || numberOfRows > MAX_NUMBER_OF_ROWS) {
		numberOfRows = MAX_NUMBER_OF_ROWS;

		for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
			pattern[row] = 0;
		}
	}
}

void savePattern()
{
	EEPROM.write(((MAX_NUMBER_OF_ROWS + 1) * patternNumber), numberOfRows);

	for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
		EEPROM.write((((MAX_NUMBER_OF_ROWS + 1) * patternNumber) + 1 + row), pattern[row]);
	}
}

void incrementClockPulseCount() {
	clockPulseCount++;
}

/*
 *  Initialise at bootup
 */

void setup()
{
	clockPulseLength = FROM_TEMPO_TO_MILLISECONDS / clockTempo; /* If you want to change the default clockTempo at the beginning, this now notices that, so you don't need to manually work out the corresponding clockPulseLength. */

	/* Setup inputs and outputs */
	pinMode(DIGITAL_PIN_CLOCK_PULSE, INPUT);
	pinMode(DIGITAL_PIN_RUN_STOP, INPUT);
	pinMode(DIGITAL_PIN_CLOCK_SOURCE, INPUT);

	for (item = 0; item < 8; item++) {
		pinMode(DIGITAL_PIN_FIRST_INSTRUMENT + item, OUTPUT);
	}

	pinMode(DIGITAL_PIN_INTERNAL_LED, OUTPUT);

	Serial.begin(115200);
	attachInterrupt(INTERRUPT_CLOCK_PULSE, incrementClockPulseCount, RISING);
	loadPattern();
}

/*
 *  Main loop
 */

void loop()
{

/*
 *  Update the clock
 */

	clockTimeAbsolute = millis();
	clockTimeRunning = clockTimeAbsolute - clockTimeAtRunStart;

	if (digitalRead(DIGITAL_PIN_CLOCK_SOURCE) == HIGH) {
		/* Use an external clock */
		clockRun = digitalRead(DIGITAL_PIN_RUN_STOP);
	} else {
		/* Use the internal clock */
		clockPulseCount = clockTimeRunning / clockPulseLength; /* The clock pulse count is absolute (being worked out anew based on a revised clock pulse length), not relative (incrementing), hence changing the tempo changes the position in the bar.  I compensate for this by only changing the *requested* tempo in real time, and updating the live tempo only at the beginning of the bar, just like pattern changes. */
	}

/*
 *  Update the sequencer and set the output for the synthesiser
 */

	if (clockRun == HIGH) {
		sequencerPulseCount = clockPulseCount % (SEQUENCER_PPSN * numberOfRows);

		if (sequencerPulseCount == 0) {
			/* We're at the very start of a pattern */
			if (patternNumber != patternNumberRequest) {
				/* Load in the queued pattern if necessary */
				patternNumber = patternNumberRequest;
				loadPattern();
			}

			if (clockTempo != clockTempoRequest) {
				/* Load in the queued tempo if necessary */
				clockTempo = clockTempoRequest;
				clockPulseLength = FROM_TEMPO_TO_MILLISECONDS / clockTempo;
				/* Reset the sequencer's clock to avoid tempo changing glitch */
				clockTimeAtRunStart = clockTimeAbsolute;
				clockTimeRunning = 0;
			}
		}

		/* Send trigger data to the synthesiser */
		/* These are triggers, not gates, so they only need to last a very short amount of time.  As it's easy to implement, we'll go with a single clock cycle. */
		if (sequencerPulseCount % SEQUENCER_PPSN == 0) {
			rowNumber = sequencerPulseCount / SEQUENCER_PPSN;

			/* Work out the current event's drums */
			for (item = 0; item < 8; item++) {
				if (pattern[rowNumber] & 1 << item) {
					digitalWrite(DIGITAL_PIN_FIRST_INSTRUMENT + item, HIGH);
				} else {
					digitalWrite(DIGITAL_PIN_FIRST_INSTRUMENT + item, LOW);
				}
			}
		} else {
			for (item = 0; item < 8; item++) {
				digitalWrite(DIGITAL_PIN_FIRST_INSTRUMENT + item, LOW);
			}
		}
	} else {
		for (item = 0; item < 8; item++) {
			digitalWrite(DIGITAL_PIN_FIRST_INSTRUMENT + item, LOW);
		}
	}

/*
 *  Set the output for everything else
 */

	/* Flash the Arduino's internal LED on every beat */
	if (rowNumber % 4 == 0) {
		digitalWrite(DIGITAL_PIN_INTERNAL_LED, HIGH);
	} else {
		digitalWrite(DIGITAL_PIN_INTERNAL_LED, LOW);
	}

	/* Update the LCD */

	/* Update the serial output only if the user's done something, or if it's the very first cycle.  See README.creole appendix C for what we're outputting. */
	if (input != NO_INPUT) {
		sprintf(hexDigit, "%02X", clockRun);
		*(output + 9) = *hexDigit;
		*(output + 10) = *(hexDigit + 1);

		sprintf(hexDigit, "%02X", clockTempoRequest);
		*(output + 13) = *hexDigit;
		*(output + 14) = *(hexDigit + 1);

		sprintf(hexDigit, "%02X", selectedInstrument);
		*(output + 17) = *hexDigit;
		*(output + 18) = *(hexDigit + 1);

		sprintf(hexDigit, "%02X", patternNumberRequest);
		*(output + 21) = *hexDigit;
		*(output + 22) = *(hexDigit + 1);

		sprintf(hexDigit, "%02X", numberOfRows);
		*(output + 25) = *hexDigit;
		*(output + 26) = *(hexDigit + 1);

		sprintf(hexDigit, "%02X", clipboardFull);
		*(output + 29) = *hexDigit;
		*(output + 30) = *(hexDigit + 1);

		for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
			sprintf(hexDigit, "%02X", pattern[row]);
			*(output + 39 + (row * 3)) = *hexDigit;
			*(output + 40 + (row * 3)) = *(hexDigit + 1);
		}

		Serial.write(output);
	}

/*
 *  Get the input
 */

	if (0) {
		/* The user's sending input via the physical buttons */
	} else if (Serial.available() > 0) {
		/* Someone or something is sending input via the serial connection.  See README.creole appendix B for what we're inputting. */
		input = Serial.read();
	} else {
		input = NO_INPUT;
	}

	switch (input) {
	case NO_INPUT:
		break;

	case RUN_STOP:
		if (clockRun == HIGH) {
			clockRun = LOW;
			sequencerPulseCount = (SEQUENCER_PPSN * numberOfRows) - 1;
		} else {
			clockRun = HIGH;
			patternNumberRequest = patternNumber;
			clockTimeAtRunStart = clockTimeAbsolute;
		}

		break;

	case DECREMENT_TEMPO:
		if (clockTempoRequest > 1) {
			clockTempoRequest--;
		}

		break;

	case INCREMENT_TEMPO:
		if (clockTempoRequest < 255) {
			clockTempoRequest++;
		}

		break;

	case DECREMENT_ROW_NUMBER:
		if (rowNumber > 0) {
			rowNumber--;
		}

		break;

	case INCREMENT_ROW_NUMBER:
		if (rowNumber < numberOfRows - 1) {
			rowNumber++;
		}

		break;

	case DECREMENT_PATTERN_NUMBER:
		savePattern();

		if (patternNumberRequest > 0) {
			patternNumberRequest--;

			if (clockRun != HIGH) {
				patternNumber = patternNumberRequest;
				loadPattern();
			}
		}

		break;

	case INCREMENT_PATTERN_NUMBER:
		savePattern();

		if (patternNumberRequest < MAX_NUMBER_OF_PATTERNS - 1) {
			patternNumberRequest++;

			if (clockRun != HIGH) {
				patternNumber = patternNumberRequest;
				loadPattern();
			}
		}

		break;

	case DECREMENT_NUMBER_OF_ROWS:
		if (numberOfRows > 1) {
			numberOfRows--;

			/* Ensure the cursor doesn't stray from the still existent rows */
			if (rowNumber > numberOfRows - 1) {
				rowNumber = numberOfRows - 1;
			}

			/* Clear the removed row */
			pattern[numberOfRows] = 0;
		}

		savePattern();
		break;

	case INCREMENT_NUMBER_OF_ROWS:
		if (numberOfRows < MAX_NUMBER_OF_ROWS) {
			numberOfRows++;
		}

		savePattern();
		break;

	case COPY_PATTERN:
		for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
			clipboard[row] = pattern[row];
		}

		clipboardNumberOfRows = numberOfRows;
		clipboardFull = HIGH;
		break;

	case PASTE_PATTERN:
		for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
			pattern[row] = clipboard[row];
		}

		numberOfRows = clipboardNumberOfRows;
		clipboardFull = LOW;
		savePattern();
		break;

	case TOGGLE_NOTE_IN_ROW_01:
	case TOGGLE_NOTE_IN_ROW_02:
	case TOGGLE_NOTE_IN_ROW_03:
	case TOGGLE_NOTE_IN_ROW_04:
	case TOGGLE_NOTE_IN_ROW_05:
	case TOGGLE_NOTE_IN_ROW_06:
	case TOGGLE_NOTE_IN_ROW_07:
	case TOGGLE_NOTE_IN_ROW_08:
	case TOGGLE_NOTE_IN_ROW_09:
	case TOGGLE_NOTE_IN_ROW_10:
	case TOGGLE_NOTE_IN_ROW_11:
	case TOGGLE_NOTE_IN_ROW_12:
	case TOGGLE_NOTE_IN_ROW_13:
	case TOGGLE_NOTE_IN_ROW_14:
	case TOGGLE_NOTE_IN_ROW_15:
	case TOGGLE_NOTE_IN_ROW_16:
		pattern[input - TOGGLE_NOTE_IN_ROW_01] ^= 1 << selectedInstrument;
		savePattern();
		break;

	case SELECT_INSTRUMENT_1:
	case SELECT_INSTRUMENT_2:
	case SELECT_INSTRUMENT_3:
	case SELECT_INSTRUMENT_4:
	case SELECT_INSTRUMENT_5:
	case SELECT_INSTRUMENT_6:
	case SELECT_INSTRUMENT_7:
	case SELECT_INSTRUMENT_8:
		selectedInstrument = input - SELECT_INSTRUMENT_1;
		break;

	case FACTORY_RESET:
		/* The user probably didn't mean to do a factory reset while playing */
		if (clockRun == HIGH) {
			break;
		}

		numberOfRows = MAX_NUMBER_OF_ROWS;

		for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
			pattern[row] = 0;
		}

		for (patternNumber = 0; patternNumber < MAX_NUMBER_OF_PATTERNS; patternNumber++) {
			savePattern();
		}

		clipboardFull = LOW;
		patternNumber = 0;
		patternNumberRequest = 0;
		rowNumber = 0;
		sequencerPulseCount = 0;
		loadPattern();
		break;
	}
}
