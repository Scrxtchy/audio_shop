import io
import os
import tempfile
import subprocess
import re


class Mangle:
	def __init__(self, infile, outfile, effects, bits = 8, blend = None, colourFormat = "rgb24", res = None):

		self.infile = infile
		self.outfile = outfile
		self.effects = effects
		self.bits = str(bits)
		self.blend = blend
		self.colourFormat = colourFormat
		self.res = res

		if not os.path.isfile(self.infile):
			MangleException("IO Error")
		if not self.bits in {"8", "16", "24"}:
			MangleException("Invalid Bits")
		self.fileResolution = self.getResolution()
		self.frames = self.getFrames()
		self.audio = self.getAudio()
		self.extractRawImage()
		if self.audio is not None:
			self.dumpAudio()
		self.processAsSound()
		if self.audio:
			self.audio = self.processAudioTrack()
		else:
			self.audio = ""
		self.recreateImage()
		self.cleanup()



	def getResolution(self):
		subPres = subprocess.Popen("ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=height,width {0}".format(self.infile), stdout=subprocess.PIPE, shell=True)
		output = subPres.communicate()[0].decode('ascii').splitlines()
		prog = re.compile(".+\=(\d+)")
		w = prog.match(output[0])[1]
		h = prog.match(output[1])[1]
		return "{0}x{1}".format(w,h)

	def getFrames(self):
		subPres = subprocess.Popen("ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of default=noprint_wrappers=1:nokey=1 {0}".format(self.infile), stdout=subprocess.PIPE, shell=True)
		output = subPres.communicate()[0].decode('ascii')
		if re.match(r'[0-9]+$', output) is not None:
			return "-frames" + output
		else:
			return ""

	def getAudio(self):
		subPres = subprocess.Popen("ffprobe -i {0} -show_streams -select_streams a -loglevel error".format(self.infile), stdout=subprocess.PIPE, shell=True)
		output = subPres.communicate()[0].decode('ascii')
		if len(output) is not 0:
			return True

	def extractRawImage(self):
		self.outputYuv = tempfile.NamedTemporaryFile(delete=True)
		self.outputYuv.name = self.outputYuv.name + ".yuv"
		if self.res is not None:
			res = "-vf scale=" + self.res.replace("x", ":")
		else:
			res = ""
		subPres = subprocess.call("ffmpeg -y -i {0} -pix_fmt {1} {2} {3}".format(self.infile, self.colourFormat, res, self.outputYuv.name), shell=True)

	def dumpAudio(self):
		self.audioIn = tempfile.NamedTemporaryFile(delete=True)
		self.audioIn.name = self.audioIn.name + ".mp3"
		subPres = subprocess.call("ffmpeg -y -i {0} -q:a 0 -map a {1}".format(self.infile, self.audioIn.name), stdout=subprocess.PIPE, shell=True)

	def processAsSound(self):
		self.audioOut = tempfile.NamedTemporaryFile(delete=True)
		self.audioOut.name = self.audioOut.name + ".u" + self.bits
		subPres = subprocess.call("sox --bits {0} -c1 -r44100 --encoding unsigned-integer -t u{0} {1} --bits {0} -c1 -r44100 --encoding unsigned-integer -t u{0} {2} {3}".format(self.bits, self.outputYuv.name, self.audioOut.name, self.effects), stdout=subprocess.PIPE, shell=True)

	def processAudioTrack(self):
		self.audioTrackOut = tempfile.NamedTemporaryFile(delete=True)
		self.audioTrackOut.name = self.audioTrackOut.name + ".mp3"
		subPres = subprocess.call("sox {0} {1} {2}".format(self.audioIn.name, self.audioTrackOut.name, self.effects), stdout=subprocess.PIPE, shell=True)
		return "-i " + self.audioTrackOut.name

	def recreateImage(self):
		if self.blend is not None:
			ffmpegOutOpts = ("-f rawvideo -pix_fmt {0} -s {1} -i {2} "
								"-filter_complex \""
								"[0:v]setpts=PTS-STARTPTS, scale={1}[top];"
								"[1:v]setpts=PTS-STARTPTS, scale={1},"
								"format=yuva444p,colorchannelmixer=aa={3}[bottom];"
								"[top][bottom]overlay=shortest=1\"").format(self.colourFormat, self.res if not "None" else self.fileResolution, self.audioOut.name, self.blend)
		else:
			ffmpegOutOpts = ""

		subPres = subprocess.call("ffmpeg -y {0} -f rawvideo -pix_fmt {1} -s {2} -i {3} {4} {5} {6}".format(ffmpegOutOpts, self.colourFormat, self.fileResolution, self.audioOut.name, self.audio, self.frames, self.outfile), stdout=subprocess.PIPE, shell=True)	
		print("command is ffmpeg -y {0} -f rawvideo -pix_fmt {1} -s {2} -i {3} {4} {5} {6}".format(ffmpegOutOpts, self.colourFormat, self.fileResolution, self.audioOut.name, self.audio, self.frames, self.outfile))
	def cleanup(self):
		self.outputYuv.close()
		if self.audio is not "":
			self.audioIn.close()
			self.audioTrackOut.close()
		self.audioOut.close()

class MangleException(Exception):
	pass