/*
 *  Stepper Acid: an acid machine with CV and gate outputs.
 *  By Zoe Blade and Nina Richards.
 */

#include "Arduino.h"
#include "EEPROM.h"
#include "Wire.h"

/*
 *  Hardware constants
 */

#define DIGITAL_PIN_CLOCK_PULSE 2
#define INTERRUPT_CLOCK_PULSE 0
#define DIGITAL_PIN_RUN_STOP 3
#define DIGITAL_PIN_GATE 4
#define DIGITAL_PIN_ACCENT 5
#define DIGITAL_PIN_CLOCK_SOURCE 6 /* Switch: LOW = internal, HIGH = external */
#define DIGITAL_PIN_INTERNAL_LED 13 /* Using an Arduino Uno, this is standard */

#define VIRGIN_MEMORY 255 /* As per http://arduino.cc/en/Reference/EEPROMRead */

/*
 *  Clock constants
 */

#define FROM_TEMPO_TO_MILLISECONDS 2500 /* 60 seconds per minute; 60 / BPM = quarter note length in seconds; 60,000 / BPM = quarter note length in milliseconds; quarter note length in milliseconds / 24 = clock pulse length in milliseconds; 60,000 / 24 = 2500; 2500 / BPM = pulse length in milliseconds */

/*
 *  Sequencer constants
 */

#define FROM_SIXTIETHS_TO_PULSES 0.1 /* Multiplying by 0.1 is the same as dividing by 60 and multiplying by 6, as in 6 PPSNs */
#define FROM_SIXTIETHS_TO_TWELVE_BITS 68.25 /* Multiplying by 68.25 is the same as dividing by 60 and multiplying by 4095 */
#define MAX_NUMBER_OF_PATTERNS 15 /* We only have 1k of EEPROM to play with */
#define MAX_NUMBER_OF_ROWS 16
#define SEMITONES_IN_OCTAVE 12
#define SEQUENCER_PPSN 6 /* 24 PPQN = 6 PPSN */

/* Array indices */
#define PITCH 0
#define SLIDE 1
#define GATE 2
#define ACCENT 3

/* Pitches */
#define C_NATURAL 0
#define C_SHARP 1
#define D_NATURAL 2
#define D_SHARP 3
#define E_NATURAL 4
#define F_NATURAL 5
#define F_SHARP 6
#define G_NATURAL 7
#define G_SHARP 8
#define A_NATURAL 9
#define A_SHARP 10
#define B_NATURAL 11

/* Note lengths */
#define REST 0
#define THIRTYSECOND 35 /* Technically, this should be 30, but apparently a certain popular acid machine uses 35. */
#define SIXTEENTH 60

/* Slide */
#define SLIDE_OFF 0
#define SLIDE_ON 60 /* For comparisons, I generally tend to use "!= SLIDE_OFF" rather than "== SLIDE_ON".  This is so I can reserve the right to make an upgrade with non-boolean sliding, so that the value of the slide dictates its length, 0 still being off or instant. */

/* Accent */
#define ACCENT_OFF 0
#define ACCENT_ON 60

/*
 *  Main constants
 */

/* Input */
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
#define TRANSPOSE_PATTERN_DOWN_SEMITONE 11
#define TRANSPOSE_PATTERN_UP_SEMITONE 12
#define TOGGLE_C_NATURAL 13
#define TOGGLE_C_SHARP 14
#define TOGGLE_D_NATURAL 15
#define TOGGLE_D_SHARP 16
#define TOGGLE_E_NATURAL 17
#define TOGGLE_F_NATURAL 18
#define TOGGLE_F_SHARP 19
#define TOGGLE_G_NATURAL 20
#define TOGGLE_G_SHARP 21
#define TOGGLE_A_NATURAL 22
#define TOGGLE_A_SHARP 23
#define TOGGLE_B_NATURAL 24
#define TRANSPOSE_NOTE_DOWN_OCTAVE 25
#define TRANSPOSE_NOTE_UP_OCTAVE 26
#define TOGGLE_SLIDE 27
#define TOGGLE_GATE 28
#define TOGGLE_ACCENT 29
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
char *output = "GLOBAL RSxxTMxxRNxxPNxxPLxxCFxx\nROW 00 PIxxSLxxGTxxACxx\nROW 01 PIxxSLxxGTxxACxx\nROW 02 PIxxSLxxGTxxACxx\nROW 03 PIxxSLxxGTxxACxx\nROW 04 PIxxSLxxGTxxACxx\nROW 05 PIxxSLxxGTxxACxx\nROW 06 PIxxSLxxGTxxACxx\nROW 07 PIxxSLxxGTxxACxx\nROW 08 PIxxSLxxGTxxACxx\nROW 09 PIxxSLxxGTxxACxx\nROW 0A PIxxSLxxGTxxACxx\nROW 0B PIxxSLxxGTxxACxx\nROW 0C PIxxSLxxGTxxACxx\nROW 0D PIxxSLxxGTxxACxx\nROW 0E PIxxSLxxGTxxACxx\nROW 0F PIxxSLxxGTxxACxx\nFOOTER\n\n";
char *hexDigit = "xx"; /* Converted to ASCII */

/* Input */
signed int input = -2; /* -2 = very first cycle, no input yet as the user hasn't had a chance; -1 = no input on this particular cycle */
unsigned char lowestPitch = 60;
unsigned char highestPitch = 0;

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

unsigned char accent = LOW;
unsigned char clipboard[MAX_NUMBER_OF_ROWS][4]; /* 4: Pitch, slide, gate, accent */
unsigned char clipboardFull = LOW;
unsigned char clipboardNumberOfRows = MAX_NUMBER_OF_ROWS;
unsigned char gate = LOW;
unsigned char lastRowNumber = 0;
unsigned char newRowNumber = 0;
unsigned char patternNumber = 0;
unsigned char patternNumberRequest = 0;
unsigned char numberOfRows = MAX_NUMBER_OF_ROWS;
unsigned char pattern[MAX_NUMBER_OF_ROWS][4]; /* 4: Pitch, slide, gate, accent */
unsigned short pitchRequest = 0; /* Used by both the sequencer and slew limiter.  The proposed pitch CV output of the slew limiter, in 12 bits. */
unsigned char rowNumber = 0;
unsigned short sequencerPulseCount = 0; /* The number of pulses that have happened so far in this pattern. */
unsigned char slide = LOW; /* Used by both the sequencer and slew limiter.  Whether the slew limiter should lag or not. */

/*
 *  Slew limiter variables
 */

unsigned long slewLimiterLastTime = 0; /* When the slew limiter was last invoked, in milliseconds */
unsigned long slewLimiterInterval = 0; /* The distance between last time and this time, in milliseconds */
unsigned short pitch = 0; /* The actual pitch CV output of the slew limiter, in 12 bits */
unsigned short slideAmount = 0; /* The difference between the requested pitch and the current pitch. */

/*
 *  Custom functions
 */

void loadPattern()
{
	numberOfRows = EEPROM.read(((MAX_NUMBER_OF_ROWS * 4) + 1) * patternNumber);

	for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
		pattern[row][PITCH] = EEPROM.read((((MAX_NUMBER_OF_ROWS * 4) + 1) * patternNumber) + 1 + (row * 4));
		pattern[row][SLIDE] = EEPROM.read((((MAX_NUMBER_OF_ROWS * 4) + 1) * patternNumber) + 2 + (row * 4)); /* Really, we're adding 1 as before to skip the pattern length, plus adding another 1 at the end to skip the pitch.  But to save processing time, let's add them together in the source code, as even though it makes no semantic sense, it makes no practical difference to do it that way. */
		pattern[row][GATE] = EEPROM.read((((MAX_NUMBER_OF_ROWS * 4) + 1) * patternNumber) + 3 + (row * 4));
		pattern[row][ACCENT] = EEPROM.read((((MAX_NUMBER_OF_ROWS * 4) + 1) * patternNumber) + 4 + (row * 4));
	}

	/* Ignore obvious errors, as in virgin EEPROM addresses */
	if (numberOfRows > MAX_NUMBER_OF_ROWS) {
		numberOfRows = MAX_NUMBER_OF_ROWS;
	}

	for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
		if (pattern[row][PITCH] > 60) {
			pattern[row][PITCH] = 24;
			pattern[row][SLIDE] = SLIDE_OFF;
			pattern[row][GATE] = REST;
			pattern[row][ACCENT] = ACCENT_OFF;
		}
	}
}

void savePattern()
{
	EEPROM.write((((MAX_NUMBER_OF_ROWS * 4) + 1) * patternNumber), numberOfRows);

	for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
		EEPROM.write(((((MAX_NUMBER_OF_ROWS * 4) + 1) * patternNumber) + 1 + (row * 4)), pattern[row][PITCH]);
		EEPROM.write(((((MAX_NUMBER_OF_ROWS * 4) + 1) * patternNumber) + 2 + (row * 4)), pattern[row][SLIDE]); /* Really, we're adding 1 as before to skip the pattern length, plus adding another 1 at the end to skip the pitch.  But to save processing time, let's add them together in the source code, as even though it makes no semantic sense, it makes no practical difference to do it that way. */
		EEPROM.write(((((MAX_NUMBER_OF_ROWS * 4) + 1) * patternNumber) + 3 + (row * 4)), pattern[row][GATE]);
		EEPROM.write(((((MAX_NUMBER_OF_ROWS * 4) + 1) * patternNumber) + 4 + (row * 4)), pattern[row][ACCENT]);
	}
}

void dacWrite(unsigned char deviceNumber, unsigned short twelveBits)
{
	unsigned char firstFourBits = twelveBits >> 4;
	unsigned char lastEightBits = twelveBits & 255;
	Wire.beginTransmission(deviceNumber);
	Wire.write(64); /* Set the DAC to receive new data. */
	Wire.write(firstFourBits);
	Wire.write(lastEightBits);
	Wire.endTransmission();
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
	Wire.begin();
	pinMode(DIGITAL_PIN_GATE, OUTPUT);
	pinMode(DIGITAL_PIN_ACCENT, OUTPUT);
	pinMode(DIGITAL_PIN_CLOCK_SOURCE, INPUT);
	pinMode(DIGITAL_PIN_CLOCK_PULSE, INPUT);
	pinMode(DIGITAL_PIN_RUN_STOP, INPUT);
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
 *  Update the sequencer
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

		/* Work out which row we're on.  If it's changed, note the last row we were on, for slides. */
		newRowNumber = sequencerPulseCount / SEQUENCER_PPSN;

		if (rowNumber != newRowNumber) {
			lastRowNumber = rowNumber;
			rowNumber = newRowNumber;
		}

		/* Work out the current event's pitch, slide, gate length and accent */
		pitchRequest = pattern[rowNumber][PITCH] * FROM_SIXTIETHS_TO_TWELVE_BITS;

		if (pattern[lastRowNumber][SLIDE] == 0) {
			slide = LOW;
		} else {
			slide = HIGH;
		}

		if (sequencerPulseCount % SEQUENCER_PPSN < pattern[rowNumber][GATE] * FROM_SIXTIETHS_TO_PULSES) {
			gate = HIGH;
		} else {
			gate = LOW;
		}

		if (pattern[rowNumber][ACCENT] > 0) {
			accent = HIGH;
		} else {
			accent = LOW;
		}
	}

/*
 *  Run the pitch through the slew limiter
 */

	slewLimiterInterval = clockTimeAbsolute - slewLimiterLastTime;
	slewLimiterLastTime = clockTimeAbsolute;

	if (slide == LOW) {
		pitch = pitchRequest;
	} else {
		/* Work out how much to change the pitch by with each iteration, but then keep that value fixed to avoid exponential slides */
		if (pitch != pitchRequest && slideAmount == 0) {
			/* Work out how far to slide in total */
			if (pitchRequest > pitch) {
				slideAmount = pitchRequest - pitch;
			} else if (pitchRequest < pitch) {
				slideAmount = pitch - pitchRequest;
			}
		}

		if (pitchRequest > pitch + (slideAmount * slewLimiterInterval * 0.05)) {
			pitch = pitch + (slideAmount * slewLimiterInterval * 0.025);
		} else if (pitchRequest < pitch - (slideAmount * slewLimiterInterval * 0.05)) {
			pitch = pitch - (slideAmount * slewLimiterInterval * 0.025);
		} else {
			/* The requested pitch has been attained.  Stop sliding. */
			pitch = pitchRequest;
			slideAmount = 0;
		}
	}

/*
 *  Set output
 */

	/* Send musical data to the synthesiser */
	dacWrite(96, pitch);
	digitalWrite(DIGITAL_PIN_GATE, gate);
	digitalWrite(DIGITAL_PIN_ACCENT, accent);

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

		sprintf(hexDigit, "%02X", rowNumber);
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
			sprintf(hexDigit, "%02X", pattern[row][PITCH]);
			*(output + 41 + (row * 24)) = *hexDigit;
			*(output + 42 + (row * 24)) = *(hexDigit + 1);

			sprintf(hexDigit, "%02X", pattern[row][SLIDE]);
			*(output + 45 + (row * 24)) = *hexDigit;
			*(output + 46 + (row * 24)) = *(hexDigit + 1);

			sprintf(hexDigit, "%02X", pattern[row][GATE]);
			*(output + 49 + (row * 24)) = *hexDigit;
			*(output + 50 + (row * 24)) = *(hexDigit + 1);

			sprintf(hexDigit, "%02X", pattern[row][ACCENT]);
			*(output + 53 + (row * 24)) = *hexDigit;
			*(output + 54 + (row * 24)) = *(hexDigit + 1);
		}

		Serial.write(output);
	}

/*
 *  Get input
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

		if (clockRun == HIGH) {
			if (patternNumberRequest > 0) {
				patternNumberRequest--;
			}
		} else {
			if (patternNumber > 0) {
				patternNumber--;
				loadPattern();
			}
		}

		break;

	case INCREMENT_PATTERN_NUMBER:
		savePattern();

		if (clockRun == HIGH) {
			if (patternNumberRequest < MAX_NUMBER_OF_PATTERNS - 1) {
				patternNumberRequest++;
			}
		} else {
			if (patternNumber < MAX_NUMBER_OF_PATTERNS - 1) {
				patternNumber++;
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
			pattern[numberOfRows][PITCH] = 24;
			pattern[numberOfRows][SLIDE] = SLIDE_OFF;
			pattern[numberOfRows][GATE] = REST;
			pattern[numberOfRows][ACCENT] = ACCENT_OFF;
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
			for (item = 0; item < 4; item++) {
				clipboard[row][item] = pattern[row][item];
			}
		}

		clipboardNumberOfRows = numberOfRows;
		clipboardFull = HIGH;
		break;

	case PASTE_PATTERN:
		for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
			for (item = 0; item < 4; item++) {
				pattern[row][item] = clipboard[row][item];
			}
		}

		numberOfRows = clipboardNumberOfRows;
		clipboardFull = LOW;
		savePattern();
		break;

	case TRANSPOSE_PATTERN_DOWN_SEMITONE:
		/* Only transpose down if every note in the pattern will still be in the 0 to 60 range afterwards */
		for (row = 0; row < numberOfRows; row++) {
			if (pattern[row][PITCH] < lowestPitch) {
				lowestPitch = pattern[row][PITCH];
			}
		}

		if (lowestPitch > 0) {
			/* Go ahead and transpose the pattern */
			for (row = 0; row < numberOfRows; row++) {
				pattern[row][PITCH]--;
			}
		}

		break;

	case TRANSPOSE_PATTERN_UP_SEMITONE:
		/* Only transpose up if every note in the pattern will still be in the 0 to 60 range afterwards */
		for (row = 0; row < numberOfRows; row++) {
			if (pattern[row][PITCH] > highestPitch) {
				highestPitch = pattern[row][PITCH];
			}
		}

		if (highestPitch < 60) {
			/* Go ahead and transpose the pattern */
			for (row = 0; row < numberOfRows; row++) {
				pattern[row][PITCH]++;
			}
		}

		break;

	case TOGGLE_C_NATURAL:
	case TOGGLE_C_SHARP:
	case TOGGLE_D_NATURAL:
	case TOGGLE_D_SHARP:
	case TOGGLE_E_NATURAL:
	case TOGGLE_F_NATURAL:
	case TOGGLE_F_SHARP:
	case TOGGLE_G_NATURAL:
	case TOGGLE_G_SHARP:
	case TOGGLE_A_NATURAL:
	case TOGGLE_A_SHARP:
	case TOGGLE_B_NATURAL:
		if (pattern[rowNumber][PITCH] % SEMITONES_IN_OCTAVE == input - TOGGLE_C_NATURAL && pattern[rowNumber][GATE] != REST) {
			pattern[rowNumber][GATE] = REST;
		} else {
			/* These two lines do the exact same thing.  Either one is fine.  I'm leaving them both here in the hope that it clarifies what's happening. */
			/* pattern[rowNumber][PITCH] = (SEMITONES_IN_OCTAVE * (pattern[rowNumber][PITCH] / SEMITONES_IN_OCTAVE)) + (input - TOGGLE_C_NATURAL); */
			pattern[rowNumber][PITCH] = pattern[rowNumber][PITCH] - (pattern[rowNumber][PITCH] % SEMITONES_IN_OCTAVE) + (input - TOGGLE_C_NATURAL); /* Keep the old octave, but update the semitone. */

			if (pattern[rowNumber][SLIDE] != SLIDE_OFF) {
				pattern[rowNumber][GATE] = SIXTEENTH;
			} else {
				pattern[rowNumber][GATE] = THIRTYSECOND;
			}
		}

		if (rowNumber < numberOfRows - 1) {
			rowNumber++;
		}

		savePattern();
		break;

	case TRANSPOSE_NOTE_DOWN_OCTAVE:
		if (pattern[rowNumber][PITCH] > 11) {
			pattern[rowNumber][PITCH] -= 12;
			savePattern();
		}

		break;

	case TRANSPOSE_NOTE_UP_OCTAVE:
		if (pattern[rowNumber][PITCH] < 49) {
			pattern[rowNumber][PITCH] += 12;
			savePattern();
		}

		break;

	case TOGGLE_SLIDE:
		if (pattern[rowNumber][SLIDE] != SLIDE_OFF) {
			pattern[rowNumber][SLIDE] = SLIDE_OFF;

			if (pattern[rowNumber][GATE] == SIXTEENTH) {
				pattern[rowNumber][GATE] = THIRTYSECOND;
			}
		} else {
			pattern[rowNumber][SLIDE] = SLIDE_ON;

			if (pattern[rowNumber][GATE] == THIRTYSECOND) {
				pattern[rowNumber][GATE] = SIXTEENTH;
			}
		}

		savePattern();
		break;

	case TOGGLE_GATE:
		if (pattern[rowNumber][GATE] == REST) {
			if (pattern[rowNumber][SLIDE] != SLIDE_OFF) {
				pattern[rowNumber][GATE] = SIXTEENTH;
			} else {
				pattern[rowNumber][GATE] = THIRTYSECOND;
			}
		} else {
			pattern[rowNumber][GATE] = REST;
		}

		savePattern();
		break;

	case TOGGLE_ACCENT:
		if (pattern[rowNumber][ACCENT] == ACCENT_OFF) {
			pattern[rowNumber][ACCENT] = ACCENT_ON;
		} else {
			pattern[rowNumber][ACCENT] = ACCENT_OFF;
		}

		savePattern();
		break;

	case FACTORY_RESET:
		/* The user probably didn't mean to do a factory reset while playing */
		if (clockRun == HIGH) {
			break;
		}

		numberOfRows = MAX_NUMBER_OF_ROWS;

		for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
			pattern[row][PITCH] = 24;
			pattern[row][SLIDE] = SLIDE_OFF;
			pattern[row][GATE] = REST;
			pattern[row][ACCENT] = ACCENT_OFF;
		}

		for (patternNumber = 0; patternNumber < MAX_NUMBER_OF_PATTERNS; patternNumber++) {
			savePattern();
		}

		clipboardFull = LOW;
		lastRowNumber = 0;
		newRowNumber = 0;
		patternNumber = 0;
		patternNumberRequest = 0;
		rowNumber = 0;
		sequencerPulseCount = 0;
		loadPattern();
		break;
	}
}
