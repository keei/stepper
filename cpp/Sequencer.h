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

public:
	void addRow() {
	}

	void copyPattern() {
	}

	void decrementCurrentChannelNumber() {
	}

	void decrementCurrentPatternNumber() {
	}

	void decrementCurrentRowNumber() {
	}

	void decrementNextPatternNumber() {
	}

	void decrementTempo() {
	}

	void getClipboardStatus() {
	}

	void getCurrentChannelNumber() {
	}

	void getCurrentPatternNumber() {
	}

	void getCurrentRowNumber() {
	}

	void getCV1InSixtieths() {
	}

	void getCV1InTwelveBits() {
	}

	void getCV2InSixtieths() {
	}

	void getCV2InTwelveBits() {
	}

	void getGateInSixtieths() {
	}

	void getGateInTwelveBits() {
	}

	void getOctave() {
	}

	void getPatternLength() {
	}

	void getPitchInSixtieths() {
	}

	void getPitchInTwelveBits() {
	}

	void getPlayMode() {
	}

	void getSemitone() {
	}

	void getSlideInSixtieths() {
	}

	char getTempo() {
		return tempo;
	}

	void incrementCurrentChannelNumber() {
	}

	void incrementCurrentPatternNumber() {
	}

	void incrementCurrentRowNumber() {
	}

	void incrementNextPatternNumber() {
	}

	void incrementTempo() {
	}

	void incrementTime() {
	}

	void loadPattern() {
	}

	void pastePattern() {
	}

	void reset() {
	}

	void savePattern() {
	}

	void setCV1() {
	}

	void setCV2() {
	}

	void setGate() {
	}

	void setOctave() {
	}

	void setPitch() {
	}

	void setPlayMode() {
	}

	void setSemitone() {
	}

	void setSlide() {
	}

	void setTempo(char tempo) {
	}

	void transposePatternDown() {
	}

	void transposePatternUp() {
	}

	Sequencer() {
		for (i = 0; i < NUMBER_OF_CHANNELS; i++) {
			cv1InSixtieths[i] = 0;
			cv1InTwelveBits[i] = 0;
			cv2InSixtieths[i] = 0;
			cv2InTwelveBits[i] = 0;
			gateInSixtieths[i] = 0;
			gateInTwelveBits[i] = 0;
			pitchInSixtieths[i] = 0;
			pitchInTwelveBits[i] = 0;
		}

		setTempo(120); // Default to 120BPM
		reset();
	}
};

#endif
