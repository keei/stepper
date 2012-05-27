/*
 *  Stepper Acid: an acid machine with CV and gate outputs.
 *  By Zoe Blade and Nina Richards.
 *
 *  Digital pin 2 is gate.
 *  Digital pin 3 is accent.
 */

#include "Arduino.h"
#include "Wire.h"

/*
 *  Clock constants
 */

#define FROM_TEMPO_TO_MILLISECONDS 625 /* 60 seconds per minute; 60 / BPM = quarter note length in seconds; 60,000 / BPM = quarter note length in milliseconds; quarter note length in milliseconds / 96 = clock pulse length in milliseconds; 60,000 / 96 = 625; 625 / BPM = pulse length in milliseconds */

/*
 *  Sequencer constants
 */

#define FROM_SIXTIETHS_TO_PULSES 0.2 /* Multiplying by 0.8 is the same as dividing by 60 and multiplying by 12, as in 12 PPSNs */
#define FROM_SIXTIETHS_TO_TWELVE_BITS 68.25 /* Multiplying by 68.25 is the same as dividing by 60 and multiplying by 4095 */
#define MAX_NUMBER_OF_ROWS 16
#define SEQUENCER_PPSN 12 /* 48 PPQN = 12 PPSN */

/* Array indeces */
#define PITCH 0
#define SLIDE 1
#define GATE 2
#define ACCENT 3

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

/*
 *  Clock variables
 */

unsigned long clockLastTime = 0; /* When the last pulse started, in milliseconds */
unsigned char clockPulse = HIGH; /* The clock pulse, 96 PPQN.  Count 1 in 2 for 48 PPQN, or 1 in 4 for 24 PPQN. */
unsigned char clockPulseStarting = HIGH; /* Whether the clock pulse is going from low to high on this exact iteration of the main loop */
unsigned long clockPulseLength = 5; /* The amount of time between one pulse start and the next, in milliseconds */
unsigned char clockRun = LOW; /* Whether or not we're running */
unsigned char clockRunRequest = LOW; /* Whether or not we're about to run */
unsigned char clockTempo = 120; /* In BPM */
unsigned long clockTime = 0; /* The current time, in milliseconds */

/*
 *  Sequencer variables
 */

unsigned char accent = LOW;
unsigned char clipboard[MAX_NUMBER_OF_ROWS][4]; /* 4: Pitch, slide, gate, accent */
unsigned char clipboardFull = LOW;
unsigned char clipboardNumberOfRows = MAX_NUMBER_OF_ROWS;
unsigned char gate = LOW;
unsigned char lastRowNumber = 0;
unsigned char newCurrentRowNumber = 0;
unsigned char patternNumber = 0;
unsigned char patternNumberRequest = 0;
unsigned char numberOfRows = MAX_NUMBER_OF_ROWS;
unsigned char pattern[MAX_NUMBER_OF_ROWS][4]; /* 4: Pitch, slide, gate, accent */
unsigned short pitchRequest = 0; /* Used by both the sequencer and slew limiter.  The proposed pitch CV output of the slew limiter, in 12 bits. */
unsigned char rowNumber = 0;
unsigned short sequencerPulseCount = 0; /* The number of pulses that have happened so far in this pattern.  Note that although the internal clock is 96 PPQN, the sequencer is only 48 PPQN.  This is so that both can be compatible with other machines. */
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
/* This ought to load the pattern.  We don't have data read/write capabilities yet.  In the meantime, let's reset the pattern, so we can at least guarantee there won't be garbage in the pattern. */
	numberOfRows = MAX_NUMBER_OF_ROWS;

	for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
		pattern[row][PITCH] = 24;
		pattern[row][SLIDE] = 0;
		pattern[row][GATE] = 0;
		pattern[row][ACCENT] = 0;
	}
}

void savePattern()
{
}

void dacWrite(unsigned char deviceNumber, unsigned short twelveBits)
{
	byte firstFourBits = twelveBits >> 4;
	byte lastEightBits = twelveBits & 255;
	Wire.beginTransmission(deviceNumber);
	Wire.write(64); /* Set the DAC to receive new data. */
	Wire.write(firstFourBits);
	Wire.write(lastEightBits);
	Wire.endTransmission();
}

/*
 *  Initialise at bootup
 */

void setup()
{
	pinMode(2, OUTPUT); /* Gate */
	pinMode(3, OUTPUT); /* Accent */
	pinMode(13, OUTPUT); /* The beat flashes the internal LED */
	loadPattern();

	/* Load a preset pattern into the first slot */
	pattern[0][PITCH] = 28;
	pattern[0][SLIDE] = 0;
	pattern[0][GATE] = 0;
	pattern[0][ACCENT] = 0;

	pattern[1][PITCH] = 28;
	pattern[1][SLIDE] = 0;
	pattern[1][GATE] = 0;
	pattern[1][ACCENT] = 0;

	pattern[2][PITCH] = 28;
	pattern[2][SLIDE] = 0;
	pattern[2][GATE] = 35;
	pattern[2][ACCENT] = 0;

	pattern[3][PITCH] = 28;
	pattern[3][SLIDE] = 0;
	pattern[3][GATE] = 0;
	pattern[3][ACCENT] = 0;

	pattern[4][PITCH] = 35;
	pattern[4][SLIDE] = 60;
	pattern[4][GATE] = 60;
	pattern[4][ACCENT] = 0;

	pattern[5][PITCH] = 40;
	pattern[5][SLIDE] = 60;
	pattern[5][GATE] = 0;
	pattern[5][ACCENT] = 0;

	pattern[6][PITCH] = 28;
	pattern[6][SLIDE] = 0;
	pattern[6][GATE] = 0;
	pattern[6][ACCENT] = 0;

	pattern[7][PITCH] = 23;
	pattern[7][SLIDE] = 0;
	pattern[7][GATE] = 35;
	pattern[7][ACCENT] = 0;

	pattern[8][PITCH] = 31;
	pattern[8][SLIDE] = 60;
	pattern[8][GATE] = 60;
	pattern[8][ACCENT] = 0;

	pattern[9][PITCH] = 16;
	pattern[9][SLIDE] = 60;
	pattern[9][GATE] = 0;
	pattern[9][ACCENT] = 0;

	pattern[10][PITCH] = 28;
	pattern[10][SLIDE] = 0;
	pattern[10][GATE] = 0;
	pattern[10][ACCENT] = 0;

	pattern[11][PITCH] = 28;
	pattern[11][SLIDE] = 0;
	pattern[11][GATE] = 35;
	pattern[11][ACCENT] = 0;

	pattern[12][PITCH] = 28;
	pattern[12][SLIDE] = 0;
	pattern[12][GATE] = 0;
	pattern[12][ACCENT] = 0;

	pattern[13][PITCH] = 28;
	pattern[13][SLIDE] = 0;
	pattern[13][GATE] = 0;
	pattern[13][ACCENT] = 0;

	pattern[14][PITCH] = 28;
	pattern[14][SLIDE] = 0;
	pattern[14][GATE] = 0;
	pattern[14][ACCENT] = 0;

	pattern[15][PITCH] = 28;
	pattern[15][SLIDE] = 0;
	pattern[15][GATE] = 0;
	pattern[15][ACCENT] = 0;
}

/*
 *  Main loop
 */

void loop()
{

/*
 *  Update the clock
 */

	clockTime = millis();

	if (clockTime - clockLastTime < clockPulseLength / 2) {
		/* The last pulse is still happening */
		clockPulse = HIGH;
		clockPulseStarting = LOW;
	} else if (clockTime - clockLastTime > clockPulseLength) {
		/* The next pulse is already happening */
		clockPulse = HIGH;
		clockLastTime = clockTime;
		clockPulseStarting = HIGH;

		/* Run/stop requests can only be fulfilled at the start of a new clock pulse */
		if (clockRunRequest == HIGH) {
			clockRun = HIGH;
		} else {
			clockRun = LOW;
		}
	} else {
		/* Neither pulse is happening */
		clockPulse = LOW;
		clockPulseStarting = LOW;
	}

/*
 *  Update the sequencer
 */

	if (clockPulseStarting == HIGH) {
		if ((oddPulse = oddPulse ^ 1) == 0) {
			/* It's an even numbered pulse.  So we're stepping down from 96 PPQN (which the clock uses) to 48 PPQN (which the sequencer uses). */
			sequencerPulseCount++;

			/* Once we reach the end of the pattern, loop back to the beginning, and load in the queued pattern if necessary. */
			if (sequencerPulseCount > SEQUENCER_PPSN * numberOfRows) {
				sequencerPulseCount = 0;

				if (patternNumber != patternNumberRequest) {
					patternNumber = patternNumberRequest;
					loadPattern();
				}
			}

			/* Work out which row we're on.  If it's changed, note the last row we were on, for slides. */
			newCurrentRowNumber = sequencerPulseCount / SEQUENCER_PPSN;

			if (newCurrentRowNumber != rowNumber) {
				lastRowNumber = rowNumber;
			}

			rowNumber = newCurrentRowNumber;

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
	}

/*
 *  Run the pitch through the slew limiter
 */

	slewLimiterInterval = clockTime - slewLimiterLastTime;
	slewLimiterLastTime = clockTime;

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

		if (pitchRequest > pitch + (slideAmount * slewLimiterInterval * 0.2)) {
			pitch = pitch + (slideAmount * slewLimiterInterval * 0.1);
		} else if (pitchRequest < pitch - (slideAmount * slewLimiterInterval * 0.2)) {
			pitch = pitch - (slideAmount * slewLimiterInterval * 0.1);
		} else {
			/* The requested pitch has been attained.  Stop sliding. */
			pitch = pitchRequest;
			slideAmount = 0;
		}
	}

/*
 *  Set output
 */

	/*dacWrite(96, pitch);*/
	digitalWrite(2, gate);
	digitalWrite(3, accent);

	/* Flash the Arduino's internal LED on every beat */
	if (rowNumber % 4 == 0) {
		digitalWrite(13, HIGH);
	} else {
		digitalWrite(13, LOW);
	}

/*
 *  Get input
 */

	if (0) { /* Toggle run/stop */
		if (clockRunRequest == HIGH) {
			clockRunRequest = LOW;
			sequencerPulseCount = (SEQUENCER_PPSN * numberOfRows) - 1;
		} else {
			clockRunRequest = HIGH;
			patternNumberRequest = patternNumber;
		}
	}

	if (0) { /* Decrement the clock's tempo */
		if (clockTempo > 1) {
			clockTempo--;
			clockPulseLength = FROM_TEMPO_TO_MILLISECONDS / clockTempo;
		}
	}

	if (0) { /* Increment the clock's tempo */
		if (clockTempo < 255) {
			clockTempo++;
			clockPulseLength = FROM_TEMPO_TO_MILLISECONDS / clockTempo;
		}
	}

	if (0) { /* Add a row to the pattern */
		if (numberOfRows < MAX_NUMBER_OF_ROWS) {
			numberOfRows++;
		}
	}

	if (0) { /* Remove a row from the pattern */
		if (numberOfRows > 1) {
			numberOfRows--;

			/* Ensure the cursor doesn't stray from the still existent rows */
			if (rowNumber > numberOfRows - 1) {
				rowNumber = numberOfRows - 1;
			}

			/* Clear the removed row */
			pattern[numberOfRows][PITCH] = 24;
			pattern[numberOfRows][SLIDE] = 0;
			pattern[numberOfRows][GATE] = 0;
			pattern[numberOfRows][ACCENT] = 0;
		}
	}

	if (0) { /* Copy a pattern to the clipboard */
		for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
			for (item = 0; item < 4; item++) {
				clipboard[row][item] = pattern[row][item];
			}
		}

		clipboardNumberOfRows = numberOfRows;
		clipboardFull = HIGH;
	}

	if (0) { /* Paste a pattern from the clipboard */
		for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
			for (item = 0; item < 4; item++) {
				pattern[row][item] = clipboard[row][item];
			}
		}

		numberOfRows = clipboardNumberOfRows;
		clipboardFull = LOW;
	}
}
