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
#define MAX_NUMBER_OF_PATTERNS 64
#define MAX_NUMBER_OF_ROWS 16
#define SEMITONES_IN_OCTAVE 12
#define SEQUENCER_PPSN 12 /* 48 PPQN = 12 PPSN */

/* Array indeces */
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
		pattern[row][SLIDE] = SLIDE_OFF;
		pattern[row][GATE] = REST;
		pattern[row][ACCENT] = ACCENT_OFF;
	}
}

void savePattern()
{
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

/*
 *  Initialise at bootup
 */

void setup()
{
	clockPulseLength = FROM_TEMPO_TO_MILLISECONDS / clockTempo; /* If you want to change the default clockTempo at the beginning, this now notices that, so you don't need to manually work out the corresponding clockPulseLength. */
/* Handy Python code to work out the scales:

for i in range(0, 48, 12):
	print(i, i+4, i+7)

for i in range(0, 48, 12):
	print(i, i+3, i+7)

*/

	unsigned char randomRootNote = 0;
	unsigned char randomMajorOrMinor = 0; /* 1 = major, 0 = minor */
	unsigned char majorScale[12] = {0,4,7,12,16,19,24,28,31,36,40,43};
	unsigned char minorScale[12] = {0,3,7,12,15,19,24,27,31,36,39,43};

	Wire.begin();
	pinMode(2, OUTPUT); /* Gate */
	pinMode(3, OUTPUT); /* Accent */
	pinMode(13, OUTPUT); /* The beat flashes the internal LED */
	loadPattern();

	/* Load a random pattern into the first slot */
	randomSeed(analogRead(0));
	randomRootNote = random(11);
	randomMajorOrMinor = random(1);

	for (row = 0; row < MAX_NUMBER_OF_ROWS; row++) {
		if (randomMajorOrMinor == 1) {
			pattern[row][PITCH] = randomRootNote + majorScale[random(11)];
		} else {
			pattern[row][PITCH] = randomRootNote + minorScale[random(11)];
		}

		pattern[row][SLIDE] = SLIDE_ON * (random(3) % 4 == 0); /* 1 in 4 chance of being SLIDE_ON, else 0 (SLIDE_OFF) */
		pattern[row][GATE] = THIRTYSECOND * (random(1) % 2 == 0); /* 1 in 2 chance of being THIRTYSECOND, else 0 (REST).  Don't just multiply THIRTYSECOND by random(1). */
		pattern[row][ACCENT] = ACCENT_ON * (random(3) % 4 == 0); /* 1 in 4 chance of being ACCENT_ON, else 0 (ACCENT_OFF) */

		/* Slides always have full length, not half length, notes.  Or no notes.  No note is fine. */
		if (pattern[row][SLIDE] == SLIDE_ON && pattern[row][GATE] == THIRTYSECOND) {
			pattern[row][GATE] = SIXTEENTH;
		}
	}
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

	if (clockPulseStarting == HIGH /* && clockRun == HIGH */) { /* For testing, pre-interface purposes, we'll pretend the musician doesn't have to press run/stop first to start the sequence. */
		if ((oddPulse = oddPulse ^ 1) == 0) {
			/* It's an even numbered pulse.  So we're stepping down from 96 PPQN (which the clock uses) to 48 PPQN (which the sequencer uses). */
			sequencerPulseCount++;

			/* Once we reach the end of the pattern, loop back to the beginning, and load in the queued pattern if necessary. */
			if (sequencerPulseCount >= SEQUENCER_PPSN * numberOfRows) {
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

	dacWrite(96, pitch);
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

	if (0) { /* Cursor up (backwards) */
		if (rowNumber > 0) {
			rowNumber--;
		}
	}

	if (0) { /* Cursor down (forwards) */
		if (rowNumber < numberOfRows - 1) {
			rowNumber++;
		}
	}

	if (0) { /* Decrement the selected (current or next) pattern */
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
	}

	if (0) { /* Increment the selected (current or next) pattern */
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
			pattern[numberOfRows][SLIDE] = SLIDE_OFF;
			pattern[numberOfRows][GATE] = REST;
			pattern[numberOfRows][ACCENT] = ACCENT_OFF;
		}

		savePattern();
	}

	if (0) { /* Add a row to the pattern */
		if (numberOfRows < MAX_NUMBER_OF_ROWS) {
			numberOfRows++;
		}

		savePattern();
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
		savePattern();
	}

	if (0) { /* Transpose pattern down a semitone */
		/* Only transpose down if every note in the pattern will still be in the 0 to 60 range afterwards */
		unsigned char lowestPitch = 60;

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
	}

	if (0) { /* Transpose pattern up a semitone */
		/* Only transpose up if every note in the pattern will still be in the 0 to 60 range afterwards */
		unsigned char highestPitch = 0;

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
	}

	/* I won't show the code for the other 11 semitones here, as there's a chance we can use a simple for-loop and forego the constant names for the semitones. */
	if (0) { /* Store a "C" note */
		if (pattern[rowNumber][PITCH] % SEMITONES_IN_OCTAVE == C_NATURAL && pattern[rowNumber][GATE] != REST) {
			pattern[rowNumber][GATE] = REST;
		} else {
			pattern[rowNumber][PITCH] = C_NATURAL;

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
	}

	if (0) { /* Move the current note down an octave */
		if (pattern[rowNumber][PITCH] > 11) {
			pattern[rowNumber][PITCH] -= 12;
			savePattern();
		}
	}

	if (0) { /* Move the current note up an octave */
		if (pattern[rowNumber][PITCH] < 49) {
			pattern[rowNumber][PITCH] += 12;
			savePattern();
		}
	}

	if (0) { /* Toggle gate between rest and slide-appropriate note length */
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
	}

	if (0) { /* Toggle accent on/off */
		if (pattern[rowNumber][ACCENT] == ACCENT_OFF) {
			pattern[rowNumber][ACCENT] = ACCENT_ON;
		} else {
			pattern[rowNumber][ACCENT] = ACCENT_OFF;
		}

		savePattern();
	}

	if (0) { /* Toggle slide on/off */
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
	}
}
