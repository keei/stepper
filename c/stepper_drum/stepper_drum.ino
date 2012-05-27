#include "Arduino.h"

/*
 *  Clock constants
 */

#define CLOCK_DEFAULT_TEMPO 120 /* In BPM */
#define CLOCK_FROM_TEMPO_TO_MILLISECONDS 625 /* 60 seconds per minute; 60 / BPM = quarter note length in seconds; 60,000 / BPM = quarter note length in milliseconds; quarter note length in milliseconds / 96 = clock pulse length in milliseconds; 60,000 / 96 = 625; 625 / BPM = pulse length in milliseconds */

/*
 *  Clock variables
 */

unsigned long clockLastTime = 0; /* When the last pulse started, in milliseconds */
unsigned char clockPulse = HIGH; /* The clock pulse, 96 PPQN.  Count 1 in 2 for 48 PPQN, or 1 in 4 for 24 PPQN. */
unsigned long clockPulseLength = 5; /* The amount of time between one pulse start and the next, in milliseconds */
unsigned char clockRun = LOW; /* Whether or not we're running */
unsigned char clockRunRequest = LOW; /* Whether or not we're about to run */
unsigned char clockTempo = CLOCK_DEFAULT_TEMPO; /* In BPM */
unsigned long clockTime = 0; /* The current time, in milliseconds */

/*
 *  Clock functions
 */

void clockDecrementTempo()
{
	if (clockTempo > 1) {
		clockTempo--;
		clockPulseLength = CLOCK_FROM_TEMPO_TO_MILLISECONDS / clockTempo;
	}
}

void clockIncrementTempo()
{
	if (clockTempo < 255) {
		clockTempo++;
		clockPulseLength = CLOCK_FROM_TEMPO_TO_MILLISECONDS / clockTempo;
	}
}

void clockSetTempo(unsigned char t)
{
	if (0 < t < 256) {
		clockTempo = t;
		clockPulseLength = CLOCK_FROM_TEMPO_TO_MILLISECONDS / clockTempo;
	}
}

void clockUpdate()
{
	clockTime = millis();

	if (clockTime - clockLastTime < clockPulseLength / 2) {
		/* The last pulse is still happening */
		clockPulse = HIGH;
	} else if (clockTime - clockLastTime > clockPulseLength) {
		/* The next pulse is already happening */
		clockPulse = HIGH;
		clockLastTime = clockTime;

		/* Run/stop requests can only be fulfilled at the start of a new clock pulse */
		if (clockRunRequest == HIGH) {
			clockRun = HIGH;
		} else {
			clockRun = LOW;
		}
	} else {
		/* Neither pulse is happening */
		clockPulse = LOW;
	}
}

/*
 *  Example main code
 */

void setup()
{
	pinMode(13, OUTPUT);
	clockSetTempo(120);
}

void loop()
{
	clockUpdate();
	digitalWrite(13, clockPulse);
}
