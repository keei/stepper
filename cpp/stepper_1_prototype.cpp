#define DEFAULT_NUMBER_OF_ROWS 16
#define MAX_NUMBER_OF_PATTERNS 64
#define MAX_NUMBER_OF_ROWS 64
#define NUMBER_OF_CHANNELS 1

// #include <iostream>
#include <stdio.h>
#include "Sequencer.cpp"

int main() {
	Sequencer sequencer;
	// std::cout << chr(sequencer.getTempo());
	// std::cout << "\n";
	printf("%u\n", sequencer.getTempo());
}
