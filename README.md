# Audio Shop
Your friendly neighborhood script for mangling images or video using audio editing tools.

If you'd like to read more about how this actually works, have a look [here](http://memcpy.io/audio-editing-images.html).

## Usage

	Place the mangler module in you pythonpath

	usage: mangleScript.py [-h] -i file -o output -e effects [--bits bits]
					 [--blend blend] [--colourFormat format] [--res resolution]
	
	Audio shop
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -i file, --input file
							Input File
	  -o output, --output output
							Output File
	  -e effects, --effects effects
							Sox effects
	  --bits bits           Audio sample rate [8/16/24]
	  --blend blend         Blend the distorted with the original [0-1]
	  --colourFormat format
							Colour format [rgb24/yuv444p/yuyv422] Full list: $ ffmpeg -pix_fmts
	  --res resolution      Output resolution [1920x1080]


	Effects:
	bass 5
	echo 0.8 0.88 60 0.4
	flanger 0 2 0 71 0.5 25 lin
	hilbert -n 5001
	loudness 6
	norm 90
	overdrive 17
	phaser 0.8 0.74 3 0.7 0.5
	phaser 0.8 0.74 3 0.4 0.5
	pitch 2
	riaa
	sinc 20-4k
	vol 10

	Example:
	./mangle.py -i in.jpg -o out.jpg -e "vol 11"
	./mangle.py -i in.mp4 -o out.mp4 -e "echo 0.8 0.88 60 0.4"
	./mangle.py -i in.mp4 -o out.mp4 -e "pitch 5" --res 1280x720
	./mangle.py -i in.mp4 -o out.mp4 -e "pitch 5" --blend 0.75 --color-format yuv444p --bits 8

	A full list of effects can be found here: http://sox.sourceforge.net/sox.html#EFFECTS

	
## Dependencies
 * ffmpeg
 * sox


## Videos
### Overdrive Hilbert
[![Alt text](/../media/apollo_b8_fyuv444p_overdrive_hilbert.gif?raw=true "Apollo 11 launch")](/../media/apollo_b8_fyuv444p_overdrive_hilbert.mp4?raw=true)

### Phaser
[![Alt text](/../media/wright_b24_frgb48be_phaser.gif?raw=true "Wright")](/../media/wright_b24_frgb48be_phaser.gif?raw=true)

## Images
### Bass
![Alt text](/../media/eiffel_tower_bass.jpg?raw=true "eiffel_tower bass")

### Echo
![Alt text](/../media/eiffel_tower_echo.jpg?raw=true "eiffel_tower echo")

### Overdrive
![Alt text](/../media/eiffel_tower_overdrive.jpg?raw=true "eiffel_tower overdrive")

### Phaser
![Alt text](/../media/eiffel_tower_phaser.jpg?raw=true "eiffel_tower phaser")

### Sinc
![Alt text](/../media/eiffel_tower_sinc.jpg?raw=true "eiffel_tower sinc")
