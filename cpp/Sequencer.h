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
	mutable bool clipboardFull, slideCV1, slideCV2, slidePitch;
	mutable char currentChannelNumber, currentPatternNumber, currentRowNumber, finalPatternNumber, nextPatternNumber, numberOfRows, playMode, tempo;
	mutable char clipboard[MAX_NUMBER_OF_ROWS * NUMBER_OF_CHANNELS], cv1InSixtieths[NUMBER_OF_CHANNELS], cv1InTwelveBits[NUMBER_OF_CHANNELS], cv2InSixtieths[NUMBER_OF_CHANNELS], cv2InTwelveBits[NUMBER_OF_CHANNELS], gateInSixtieths[NUMBER_OF_CHANNELS], gateInTwelveBits[NUMBER_OF_CHANNELS], patternInSixtieths[MAX_NUMBER_OF_ROWS * NUMBER_OF_CHANNELS], pitchInSixtieths[NUMBER_OF_CHANNELS], pitchInTwelveBits[NUMBER_OF_CHANNELS], ;
};

#endif
