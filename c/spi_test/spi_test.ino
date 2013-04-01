/*
 *  SPI bus test
 *  Using our custom protocol
 *
 *  MOSI: 64 bits / 8 bytes for LEDs; 16 bits / 2 bytes for seven segment display
 *  MISO: 64 bits / 8 bytes for buttons; 8 bits / 1 byte for rotary encoder; 8 bits / 1 byte all zeroes, or for a second rotary encoder
 *
 *  A simple test program, based on Nick Gammon's SPI bus testing example
 */

#include <SPI.h>

unsigned char i = 0;
unsigned char j = 0;
unsigned char r[10] = {0,0,0,0,0,0,0,0,0,0}; /* R for return (what the slave tells the master) */

void setup()
{
	digitalWrite(SS, HIGH);
	SPI.begin();
	SPI.setClockDivider(SPI_CLOCK_DIV64);
	Serial.begin(115200);
}

void loop()
{
	for (i = 0; i < 64; i++) {
		digitalWrite(SS, LOW); /* Start communication */

		/* Light up the LEDs in sequence */
		for (j = 0; j < 8; j++) {
			if (j == (i / 8)) {
				r[j] = SPI.transfer(1 << i % 8);
			} else {
				r[j] = SPI.transfer(0);
			}
		}

		/* Send a number to the seven segment LCD */
		r[8] = SPI.transfer(0); /* It only counts up to 63, which is decidedly less than 255 */
		r[9] = SPI.transfer(i);

		digitalWrite(SS, HIGH); /* Stop communication */

		/* Echo out the returned information as if it's ASCII */
		for (j = 0; j < 10; j++) {
			Serial.println(r[j], HEX);
		}

		Serial.write("\n");
		delay(500);
	}
}
