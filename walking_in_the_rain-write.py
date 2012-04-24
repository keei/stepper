import surf

# Walking In the Rain

sequencer = surf.Sequencer()
sequencer.setTempo(120)
sequencer.setSongName('Walking in the Rain')
sequencer.setArtistName('Zoë Blade')
sequencer.setArtistEmailAddress('zoe@bytenoise.co.uk')
sequencer.setSongInformation('Good to test Surf with.')

pattern = open('walking_in_the_rain.txt')

for eventRow in pattern:
	sequencer.addEventRow(eventRow)

sequencer.saveSong('walking_in_the_rain.xml')
