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

#ifndef PITCH
#define PITCH 0
#endif

#ifndef SLIDE
#define SLIDE 1
#endif

#ifndef GATE
#define GATE 2
#endif

#ifndef CV1
#define CV1 3
#endif

#ifndef CV2
#define CV2 4
#endif

class Sequencer {
private:
	mutable float averageRowLengthInSeconds;
	mutable unsigned char clipboard[MAX_NUMBER_OF_ROWS][NUMBER_OF_CHANNELS][5];
	mutable bool clipboardFull;
	mutable unsigned char currentChannelNumber;
	mutable unsigned char currentPatternNumber;
	mutable unsigned char currentRowNumber;
	mutable unsigned short cv1InTwelveBits[NUMBER_OF_CHANNELS];
	mutable unsigned short cv2InTwelveBits[NUMBER_OF_CHANNELS];
	mutable unsigned char finalPatternNumber;
	mutable unsigned short gateInTwelveBits[NUMBER_OF_CHANNELS];
	mutable unsigned char i;
	mutable unsigned char nextPatternNumber;
	mutable unsigned char numberOfRows;
	mutable float patternPositionInSeconds;
	mutable unsigned char patternInSixtieths[MAX_NUMBER_OF_ROWS][NUMBER_OF_CHANNELS][5];
	mutable unsigned short pitchInTwelveBits[NUMBER_OF_CHANNELS];
	mutable unsigned char playMode;
	mutable unsigned char tempo;
	mutable float timeInSeconds;

public:
	mutable bool slideCV1;
	mutable bool slideCV2;
	mutable bool slidePitch;

	Sequencer() {
		for (i = 0; i < NUMBER_OF_CHANNELS; i++) {
			cv1InTwelveBits[i] = 0;
			cv2InTwelveBits[i] = 0;
			gateInTwelveBits[i] = 0;
			pitchInTwelveBits[i] = 0;
		}

		setTempo(120); // Default to 120BPM
		reset();
	}

	void addRow() {
		if (numberOfRows < MAX_NUMBER_OF_ROWS) {
			numberOfRows++;
		}
	}

	void copyPattern() {
		// clipboard = patternInSixtieths;
		clipboardFull = true;
	}

	void decrementCurrentChannelNumber() {
		if (currentChannelNumber > 0) {
			currentChannelNumber--;
		}
	}

	void decrementCurrentPatternNumber() {
		if (currentPatternNumber > 0) {
			currentPatternNumber--;
		}
	}

	void decrementCurrentRowNumber() {
		if (currentRowNumber > 0) {
			currentRowNumber--;
		}
	}

	void decrementNextPatternNumber() {
		if (nextPatternNumber > 0) {
			nextPatternNumber--;
		}
	}

	void decrementTempo() {
		if (tempo > 1) {
			setTempo(tempo - 1);
		}
	}

	bool getClipboardStatus() {
		return clipboardFull;
	}

	unsigned char getCurrentChannelNumber() {
		return currentChannelNumber;
	}

	unsigned char getCurrentPatternNumber() {
		return currentPatternNumber;
	}

	unsigned char getCurrentRowNumber() {
		return currentRowNumber;
	}

	unsigned char getCV1InSixtieths() {
		return patternInSixtieths[currentRowNumber][currentChannelNumber][CV1];
	}

	unsigned short getCV1InTwelveBits(unsigned char c) {
		return cv1InTwelveBits[c];
	}

	unsigned char getCV2InSixtieths() {
		return patternInSixtieths[currentRowNumber][currentChannelNumber][CV2];
	}

	unsigned short getCV2InTwelveBits(unsigned char c) {
		return cv2InTwelveBits[c];
	}

	unsigned char getGateInSixtieths() {
		return patternInSixtieths[currentRowNumber][currentChannelNumber][GATE];
	}

	unsigned short getGateInTwelveBits(unsigned char c) {
		return gateInTwelveBits[c];
	}

	unsigned char getOctave() {
	}

	unsigned char getPatternLength() {
		return numberOfRows;
	}

	unsigned char getPitchInSixtieths() {
		return patternInSixtieths[currentRowNumber][currentChannelNumber][PITCH];
	}

	unsigned short getPitchInTwelveBits(unsigned char c) {
		return pitchInTwelveBits[c];
	}

	unsigned char getPlayMode() {
		return playMode;
	}

	unsigned char getSemitone() {
	}

	unsigned char getSlideInSixtieths() {
	}

	char getTempo() {
		return tempo;
	}

	void incrementCurrentChannelNumber() {
		if (currentChannelNumber < NUMBER_OF_CHANNELS - 1) {
			currentChannelNumber++;
		}
	}

	void incrementCurrentPatternNumber() {
		if (currentPatternNumber < MAX_NUMBER_OF_PATTERNS - 1) {
			currentPatternNumber++;
		}
	}

	void incrementCurrentRowNumber() {
		if (currentRowNumber < numberOfRows - 1) {
			currentRowNumber++;
		}
	}

	void incrementNextPatternNumber() {
		if (nextPatternNumber < MAX_NUMBER_OF_PATTERNS - 1) {
			nextPatternNumber++;
		}
	}

	void incrementTempo() {
		if (tempo < 255) {
			setTempo(tempo + 1);
		}
	}

	void incrementTime() {
	}

	void loadPattern() {
	}

	void pastePattern() {
		// patternInSixtieths = clipboard;
		// clipboard = [];
		clipboardFull = false;
	}

	void removeRow() {
		if (numberOfRows > 1) {
			numberOfRows--;
		}

		// Actually wipe the old row clean
	}

	void reset() {
	}

	void savePattern() {
	}

	void setCV1(unsigned char c) {
		patternInSixtieths[currentRowNumber][currentChannelNumber][CV1] = c;
	}

	void setCV2(unsigned char c) {
		patternInSixtieths[currentRowNumber][currentChannelNumber][CV2] = c;
	}

	void setGate(unsigned char g) {
		patternInSixtieths[currentRowNumber][currentChannelNumber][GATE] = g;
	}

	void setOctave(unsigned char o) {
	}

	void setPitch(unsigned char p) {
		patternInSixtieths[currentRowNumber][currentChannelNumber][PITCH] = p;
	}

	void setPlayMode(unsigned char p) {
		playMode = p;
	}

	void setSemitone(unsigned char s) {
	}

	void setSlide(unsigned char s) {
		patternInSixtieths[currentRowNumber][currentChannelNumber][SLIDE] = s;
	}

	void setTempo(char t) {
		tempo = t;
	}

	void transposePatternDown() {
	}

	void transposePatternUp() {
	}
};

#endif
