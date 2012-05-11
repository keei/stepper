#define DEFAULT_NUMBER_OF_ROWS 16
#define MAX_NUMBER_OF_PATTERNS 64
#define MAX_NUMBER_OF_ROWS 64
#define NUMBER_OF_CHANNELS 1

#include <curses.h>
#include <stdio.h>
#include <time.h>
#include "Sequencer.cpp"

unsigned char i;

void cursePrint(unsigned char rowNumber, unsigned char firstColumnNumber, char string[80], bool invert) {
	for (i = 0; i < sizeof(string); i++) {
		if (invert == true) {
			addch(rowNumber, columnNumber + i, string[i], A_REVERSE);
		} else {
			addch(rowNumber, columnNumber + i, string[i]);
		}
	}
}

long millis() {
	return clock();
}

int main() {
	unsigned short previousCycleTimeInSeconds = 0;
	unsigned short timeInMiliseconds = 0;
	char key = '.';

	Sequencer sequencer;
	sequencer.slideCV1 = false; // This won't have a DAC
	sequencer.slideCV2 = false; // This won't exist at all

	initscr();
	noecho();

	while (true) {
		key = getch();

		if (key == ' ') {
			endwin();
			return 0;
		}

		timeInMiliseconds = millis();
		cursePrint(0, 0, 'test', false);
	}
}
