class NotationToCVConverter:
	temperament = '12e'
	noteTable = ['c', 'cs', 'd', 'ds', 'e', 'f', 'fs', 'g', 'gs', 'a', 'as', 'b']

	def __init__(self):
		pass

	def convert(self, note):
		if self.temperament == '12e':
			noteLetter = note[:-1]
			noteOctave = int(note[-1:])
			noteOctave = noteOctave - 1
			noteNumber = self.noteTable.index(noteLetter)
			return noteOctave + (1 / 12 * noteNumber)
