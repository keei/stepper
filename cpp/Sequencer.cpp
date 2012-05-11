#include "Sequencer.h"

	Sequencer::Sequencer() {
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

	char Sequencer::getTempo() {
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

	void Sequencer::reset() {
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

	void Sequencer::setTempo(char tempo) {
	}

	void transposePatternDown() {
	}

	void transposePatternUp() {
	}
