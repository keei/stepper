#define DEFAULT_NUMBER_OF_ROWS 16
#define MAX_NUMBER_OF_PATTERNS 64
#define MAX_NUMBER_OF_ROWS 16
#define NUMBER_OF_CHANNELS 1

#include <Wire.h> // http://arduino.cc/it/Reference/Wire
#include "Sequencer.cpp"

void updateDac(short twelveBits) {
	byte firstFourBits = twelveBits >> 4;
	byte lastEightBits = twelveBits & 255;
	Wire.beginTransmission(96);
	Wire.write(64); // Set the DAC to receive new data.
	Wire.write(firstFourBits);
	Wire.write(lastEightBits);
	Wire.endTransmission();
}

void setup() {
	Wire.begin();
}

void loop() {
}
