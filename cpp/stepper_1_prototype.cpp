#define DEFAULT_NUMBER_OF_ROWS 16
#define MAX_NUMBER_OF_PATTERNS 64
#define MAX_NUMBER_OF_ROWS 64
#define NUMBER_OF_CHANNELS 1

#include <stdio.h>
#include "Sequencer.cpp"

int main() {
	unsigned short previousCycleTimeInSeconds = 0;
	char key = ' ';

	Sequencer sequencer;
	sequencer.slideCV1 = false; // This won't have a DAC
	sequencer.slideCV2 = false; // This won't exist at all

	while (key = getchar()) {
		if (key == 'q') {
			return 0;
		}

		printf("Pitch: %u\n", sequencer.getPitchInTwelveBits(0));
		printf("Gate:  %u\n", sequencer.getGateInTwelveBits(0));
		printf("CV1:   %u\n", sequencer.getCV1InTwelveBits(0));
		printf("CV1:   %u\n", sequencer.getCV2InTwelveBits(0));
	}
}
