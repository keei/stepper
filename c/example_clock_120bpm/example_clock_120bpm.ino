#include "Arduino.h"

/*
 *  Clock constants
 */

#define DEFAULT_TEMPO 120 /* In BPM */
#define FROM_TEMPO_TO_MILLISECONDS 625 /* 60 seconds per minute; 60 / BPM = quarter note length in seconds; 60,000 / BPM = quarter note length in milliseconds; quarter note length in milliseconds / 96 = clock pulse length in milliseconds; 60,000 / 96 = 625; 625 / BPM = pulse length in milliseconds */

/*
 *  Clock variables
 */

unsigned long lastTime = 0; /* When the last pulse started, in milliseconds */
unsigned char pulse = HIGH; /* The clock pulse, 96 PPQN.  Count 1 in 2 for 48 PPQN, or 1 in 4 for 24 PPQN. */
unsigned long pulseLength = 5; /* The amount of time between one pulse start and the next, in milliseconds */
unsigned char run = LOW; /* Whether or not we're running */
unsigned char runRequest = LOW; /* Whether or not we're about to run */
unsigned char tempo = DEFAULT_TEMPO; /* In BPM */
unsigned long time = 0; /* The current time, in milliseconds */

/*
 *  Clock functions
 */

void decrementTempo()
{
	if (tempo > 1) {
		tempo--;
		pulseLength = FROM_TEMPO_TO_MILLISECONDS / tempo;
	}
}

void incrementTempo()
{
	if (tempo < 255) {
		tempo++;
		pulseLength = FROM_TEMPO_TO_MILLISECONDS / tempo;
	}
}

void setTempo(unsigned char t)
{
	if (0 < t < 256) {
		tempo = t;
		pulseLength = FROM_TEMPO_TO_MILLISECONDS / tempo;
	}
}

void updateStepperClock()
{
	time = millis();

	if (time - lastTime < pulseLength / 2) {
		/* The last pulse is still happening */
		pulse = HIGH;
	} else if (time - lastTime > pulseLength) {
		/* The next pulse is already happening */
		pulse = HIGH;
		lastTime = time;

		/* Run/stop requests can only be fulfilled at the start of a new clock pulse */
		if (runRequest == HIGH) {
			run = HIGH;
		} else {
			run = LOW;
		}
	} else {
		/* Neither pulse is happening */
		pulse = LOW;
	}
}

/*
 *  Example main code
 */

void setup()
{
	pinMode(13, OUTPUT);
	setTempo(120);
}

void loop()
{
	updateStepperClock();
	digitalWrite(13, pulse);
}
