#ifndef SEQUENCER_H
#define SEQUENCER_H

#ifndef DEFAULT_NUMBER_OF_ROWS
#define DEFAULT_NUMBER_OF_ROWS 64
#endif

#ifndef MAX_NUMBER_OF_PATTERNS
#define MAX_NUMBER_OF_PATTERNS 64
#endif

#ifndef MAX_NUMBER_OF_ROWS
#define MAX_NUMBER_OF_ROWS 64
#endif

#ifndef NUMBER_OF_CHANNELS
#define NUMBER_OF_CHANNELS 4
#endif

class Sequencer {
private:
	mutable float averageRowLengthInSeconds;
	mutable char clipboard[MAX_NUMBER_OF_ROWS * NUMBER_OF_CHANNELS];
	mutable bool clipboardFull;
	mutable char currentChannelNumber;
	mutable char currentPatternNumber;
	mutable char currentRowNumber;
	mutable char cv1InSixtieths[NUMBER_OF_CHANNELS];
	mutable char cv1InTwelveBits[NUMBER_OF_CHANNELS];
	mutable char cv2InSixtieths[NUMBER_OF_CHANNELS];
	mutable char cv2InTwelveBits[NUMBER_OF_CHANNELS];
	mutable char finalPatternNumber;
	mutable char gateInSixtieths[NUMBER_OF_CHANNELS];
	mutable char gateInTwelveBits[NUMBER_OF_CHANNELS];
	mutable char i;
	mutable char nextPatternNumber;
	mutable char numberOfRows;
	mutable float patternPositionInSeconds;
	mutable char patternInSixtieths[MAX_NUMBER_OF_ROWS * NUMBER_OF_CHANNELS];
	mutable char pitchInSixtieths[NUMBER_OF_CHANNELS];
	mutable char pitchInTwelveBits[NUMBER_OF_CHANNELS];
	mutable char playMode;
	mutable bool slideCV1;
	mutable bool slideCV2;
	mutable bool slidePitch;
	mutable char tempo;
	mutable float timeInSeconds;
};

#endif
