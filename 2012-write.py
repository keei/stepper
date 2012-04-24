import surf

# 2012

sequencer = surf.Sequencer()
sequencer.setTempo(118)
sequencer.setSongName('2012')
sequencer.setArtistName('Zoë Blade ft. Snowflake')
sequencer.setArtistEmailAddress('zoe@bytenoise.co.uk')
sequencer.setSongInformation('Good to test Surf with.')

pattern = open('2012.txt')

for eventRow in pattern:
	sequencer.addEventRow(eventRow)

sequencer.saveSong('2012.xml')
