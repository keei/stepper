#define DEFAULT_NUMBER_OF_ROWS 16
#define MAX_NUMBER_OF_PATTERNS 64
#define MAX_NUMBER_OF_ROWS 64
#define NUMBER_OF_CHANNELS 1

#include <curses.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "Sequencer.cpp"


void cursePrint(unsigned char rowNumber, unsigned char firstColumnNumber, char s[81], bool invert) {
	unsigned char i;

	for (i = 0; i < strlen(s); i++) {
		if (invert == true) {
			move(rowNumber, firstColumnNumber + i);
			addch(s[i]);
		} else {
			move(rowNumber, firstColumnNumber + i);
			addch(s[i]);
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
		cursePrint(0, 0, "test", false);
	}
}
