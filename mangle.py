import argparse
import io
import os.path
import tempfile
import subprocess
import re

def main():
	arg = argparse.ArgumentParser(description="Audio shop")

	arg.add_argument("-i", "--input",
					metavar = "file",
					type = str,
					required = True,
					help = "Input File")
	arg.add_argument("-o", "--output",
					metavar = "output",
					type = str,
					required = True,
					help = "Output File")
	arg.add_argument("-e", "--effects",
					metavar = "effects",
					type = str,
					required = True,
					help = "Sox effects")
	arg.add_argument("--bits",
					metavar = "bits",
					type = int,
					help = "Audio sample rate [8/16/24]")
	arg.add_argument("--blend",
					metavar = "blend",
					type = float,
					help = "Blend the distorted with the original [0-1]")
	arg.add_argument("--colourFormat",
					metavar="format",
					type = str,
					help = "Colour format [rgb24/yuv444p/yuyv422] Full list: $ ffmpeg -pix_fmts")
	arg.add_argument("--res",
					metavar="resolution",
					type = str,
					help = "Output resolution [1920x1080]")

	global args
	global meta
	global FFMPEG_IN_OPTS
	global FFMPEG_OUT_OPTS
	global defaultVars

	args = arg.parse_args()
	defaultVars = {'bits': '8', 'YUV_FMT':'rgb24'}
	FFMPEG_IN_OPTS = ""
	FFMPEG_OUT_OPTS = ""
	meta = {}
	FNULL = open(os.devnull, 'w')
	


	parseArgs()
	getResolution()
	getFrames()
	getAudio()

	print("TMP_DIR:         $TMP_DIR")
	print("RES:             $RES")
	print("VIDEO:           $VIDEO")
	print("AUDIO:           $AUDIO")
	print("FFMPEG_IN_OPTS:  $(eval echo " + FFMPEG_IN_OPTS +")")
	print("FFMPEG_OUT_OPTS: $(eval echo " + FFMPEG_OUT_OPTS +")")
	print("SOX_OPTS:        $(eval echo " + args.effects + ")")

	print("Extracting raw image data")

	outputYuv = tempfile.NamedTemporaryFile()
	outputYuv.name = outputYuv.name + ".yuv"
	subPres = subprocess.call("ffmpeg -y -i {0} -pix_fmt {1} {2} {3}".format(args.input, defaultVars['YUV_FMT'], FFMPEG_IN_OPTS, outputYuv.name), shell=True)
	print("Extracted raw image")


	if len(meta['audio']) is not 0:
		audioIn = tempfile.NamedTemporaryFile()
		audioIn.name = audioIn.name + ".mp3"
		meta['audio'] = '-i' + audioIn.name
		subPres = subprocess.call("ffmpeg -y -i %s  -q:a 0 -map a %s" %(args.input, audioIn.name), stdout=subprocess.PIPE, shell=True)

	print("Processing as sound")

	# outputYuv.name = outputYuv.name + ".u" + defaultVars['bits']
	# print("moved output yuv file")
	# print(outputYuv.name)
	audioOut = tempfile.NamedTemporaryFile()
	audioOut.name = audioOut.name + ".u" + defaultVars['bits']
	subPres = subprocess.call("sox --bits {0} -c1 -r44100 --encoding unsigned-integer -t u{0} {1} --bits {0} -c1 -r44100 --encoding unsigned-integer -t u{0} {2} {3}".format(defaultVars['bits'], outputYuv.name, audioOut.name, args.effects), stdout=subprocess.PIPE, shell=True)
	if len(meta['audio']) is not 0:
		print("Processing audio track as sound")
		uselessAudioOut = tempfile.NamedTemporaryFile()
		subPres = subprocess.call("sox {0} {1} {2}" %(audioIn.name,uselessAudioOut.name, args.effects), stdout=subprocess.PIPE, shell=True)

	print("Recreating image from audio")
	subPres = subprocess.call("ffmpeg -y {0} -f rawvideo -pix_fmt {1} -s {2} -i {3} {4} {5} {6}".format(FFMPEG_OUT_OPTS, defaultVars['YUV_FMT'], meta['res'],audioOut.name, meta['audio'], str(meta['video']), args.output ), stdout=subprocess.PIPE, shell=True)	

	FNULL.close()
	outputYuv.close()
	if len(meta['audio']) is not 0:
		audioIn.close()
		uselessAudioOut.close()
	audioOut.close()
	


def parseArgs():
	if args.res:
		FFMPEG_IN_OPTS = FFMPEG_IN_OPTS + args.res.replace("x", ":")
	if args.bits:
		defaultVars['bits'] = bits
	if args.blend:
		#FFMPEG_OUT_OPTS = FFMPEG_OUT_OPTS +
		print("TODO")
		#"-f rawvideo -pix_fmt \$YUV_FMT -s \${RES} -i \${TMP_DIR}/tmp_audio_out.\${S_TYPE}"+
		#"-filter_complex" +
		#"[0:v]setpts=PTS-STARTPTS, scale=\${RES}[top]\;" +
		#"[1:v]setpts=PTS-STARTPTS, scale=\${RES}," + 
		#"format=yuva444p,colorchannelmixer=aa=${BLEND}[bottom]\;"+
		#"[top][bottom]overlay=shortest=1"
	if args.colourFormat:
		defaultVars['YUV_FMT'] = args.colour-format



def getResolution():
	subPres = subprocess.Popen("ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=height,width %s" % args.input, stdout=subprocess.PIPE, shell=True)
	output = subPres.communicate()[0].decode('ascii').splitlines()
	prog = re.compile(".+\=(\d+)")
	w = prog.match(output[0])[1]
	h = prog.match(output[1])[1]

	print(output)
	meta['res'] = "{0}x{1}".format(w,h)
	

def getFrames():
	subPres = subprocess.Popen("ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=noprint_wrappers=1:nokey=1  %s" % args.input, stdout=subprocess.PIPE, shell=True)
	output = subPres.communicate()[0].decode('ascii')
	print('FRAMES;'+ output)
	if re.match(r'^[0-9]+$', output) is not None:
		meta['video'] = '-frames ' + output
	else:
		meta['video'] = ""

def getAudio():
	subPres = subprocess.Popen("ffprobe -i %s -show_streams -select_streams a -loglevel error" % args.input, stdout=subprocess.PIPE, shell=True)
	(output, err) = subPres.communicate()
	meta['audio'] = output.decode('ascii')
	if len(output) is not 0:
		print('Audio will be dumped')

if __name__ == "__main__":
	main()
