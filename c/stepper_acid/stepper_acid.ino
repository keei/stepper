#include "Arduino.h"

/*
 *  Clock constants
 */

#define CLOCK_FROM_TEMPO_TO_MILLISECONDS 625 /* 60 seconds per minute; 60 / BPM = quarter note length in seconds; 60,000 / BPM = quarter note length in milliseconds; quarter note length in milliseconds / 96 = clock pulse length in milliseconds; 60,000 / 96 = 625; 625 / BPM = pulse length in milliseconds */

/*
 *  Sequencer constants
 */

#define SEQUENCER_PPSN 12 /* 48 PPQN = 12 PPSN */

/*
 *  Main variables
 */

unsigned char oddPulse = 1; /* Think of it as starting at -1 */

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

unsigned char currentPatternNumber = 0;
unsigned char currentRowNumber = 0;
unsigned char lastRowNumber = 0;
unsigned char newCurrentRowNumber = 0;
unsigned char nextPatternNumber = 0;
unsigned char numberOfRows = 16;
unsigned int sequencerPulseCount = 0; /* The number of pulses that have happened so far in this pattern.  Note that although the internal clock is 96 PPQN, the sequencer is only 48 PPQN.  This is so that both can be compatible with other machines. */

/*
 *  Slew limiter variables
 */

unsigned long slewLimiterLastTime = 0; /* When the slew limiter was last invoked, in milliseconds */
unsigned long slewLimiterInterval = 0; /* The distance between last time and this time, in milliseconds */
unsigned char slewLimiterPitch = 0; /* The actual pitch CV output of the slew limiter, in 12 bits */
unsigned char pitchRequest = 0; /* The proposed pitch CV output of the slew limiter, in 12 bits */
unsigned char slide = 0; /* Whether the slew limiter should lag or not */

/*
 *  Custom functions
 */

void loadPattern()
{
}

void savePattern()
{
}

/*
 *  Initialise at bootup
 */

void setup()
{
	pinMode(13, OUTPUT);
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
		oddPulse = oddPulse ^ 1; /* I'm guessing there's no such thing as "oddPulse =^ 1"? */

		if (oddPulse == 0) {
			sequencerPulseCount++;

			if (sequencerPulseCount > SEQUENCER_PPSN * numberOfRows) {
				sequencerPulseCount = 0;
				currentPatternNumber = nextPatternNumber;
				loadPattern();
			}

			newCurrentRowNumber = sequencerPulseCount / SEQUENCER_PPSN;

			if (newCurrentRowNumber != currentRowNumber) {
				lastRowNumber = currentRowNumber;
			}

			currentRowNumber = newCurrentRowNumber;
		}
	}

/*
 *  Run the pitch through the slew limiter
 */

/* Make sure pitchRequest and slide are set appropriately by the sequencer first */
	slewLimiterInterval = clockTime - slewLimiterLastTime;
	slewLimiterLastTime = clockTime;

	if (slide == 0) {
		slewLimiterPitch = pitchRequest;
	} else {
		if (pitchRequest > slewLimiterPitch + (slewLimiterInterval * 2)) {
			slewLimiterPitch = slewLimiterPitch + slewLimiterInterval;
		} else if (pitchRequest < slewLimiterPitch - (slewLimiterInterval * 2)) {
			slewLimiterPitch = slewLimiterPitch - slewLimiterInterval;
		} else {
			slewLimiterPitch = pitchRequest;
		}
	}

/*
 *  Set output
 */

	/* Flash the Arduino's internal LED on every beat */
	if (currentRowNumber % 4 == 0) {
		digitalWrite(13, HIGH);
	} else {
		digitalWrite(13, LOW);
	}

/*
 *  Get input
 */

	if (0) { /* Decrement the clock's tempo */
		if (clockTempo > 1) {
			clockTempo--;
			clockPulseLength = CLOCK_FROM_TEMPO_TO_MILLISECONDS / clockTempo;
		}
	}

	if (0) { /* Increment the clock's tempo */
		if (clockTempo < 255) {
			clockTempo++;
			clockPulseLength = CLOCK_FROM_TEMPO_TO_MILLISECONDS / clockTempo;
		}
	}
}
