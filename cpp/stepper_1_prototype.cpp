#define DEFAULT_NUMBER_OF_ROWS 16
#define MAX_NUMBER_OF_PATTERNS 64
#define MAX_NUMBER_OF_ROWS 64
#define NUMBER_OF_CHANNELS 1

#include <curses.h>
#include <stdio.h>
#include <string.h>
#include <sys/time.h>
#include "Sequencer.cpp"

struct timeval tv;
unsigned long startTimeInMiliseconds = 0;

void cursePrint(unsigned char rowNumber, unsigned char firstColumnNumber, char s[81], bool invert) {
	unsigned char i;

	if (invert == true) {
		attron(A_REVERSE);
	}

	for (i = 0; i < strlen(s); i++) {
		mvaddch(rowNumber, firstColumnNumber + i, s[i]);
	}

	if (invert == true) {
		attron(A_REVERSE);
	}
}

long millis() {
	gettimeofday(&tv, NULL);
	return (tv.tv_sec * 1000) + tv.tv_usec - startTimeInMiliseconds;
}

int main() {
	unsigned short previousCycleTimeInSeconds = 0;
	unsigned short timeInMiliseconds = 0;
	char key = '.';

	gettimeofday(&tv, NULL);
	startTimeInMiliseconds = (tv.tv_sec * 1000) + tv.tv_usec;

	Sequencer sequencer;
	sequencer.slideCV1 = false; // This won't have a DAC
	sequencer.slideCV2 = false; // This won't exist at all

	initscr();
	nodelay(stdscr, true);
	noecho();
	cbreak();
	timeout(-1);

	while (true) {
		key = getch();

		if (key == ' ') {
			endwin();
			timeInMiliseconds = millis();
			printf("Time in miliseconds: %u\n", timeInMiliseconds);
			return 0;
		}

		timeInMiliseconds = millis();
		cursePrint(0, 0, "test", false);
		refresh();
	}
}
