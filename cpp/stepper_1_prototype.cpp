#define DEFAULT_NUMBER_OF_ROWS 16
#define MAX_NUMBER_OF_PATTERNS 64
#define MAX_NUMBER_OF_ROWS 64
#define NUMBER_OF_CHANNELS 1

#include <curses.h>
#include <stdio.h>
#include "Sequencer.cpp"

int main() {
	unsigned short previousCycleTimeInSeconds = 0;

	Sequencer sequencer;
	sequencer.slideCV1 = false; // This won't have a DAC
	sequencer.slideCV2 = false; // This won't exist at all

	initscr();

	while (true) {
		if (true) {
			endwin();
		}
	}
}
