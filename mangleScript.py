from mangle import Mangle
import argparse

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
	args = arg.parse_args()
	Mangle(args.input, args.output, args.effects, bits=args.bits if not None else 8, blend=args.blend, colourFormat="rgb24", res=args.res)
	
	#def __init__(self, infile, outfile, effects, bits = 8, blend = None, colourFormat = "rgb24", res = None):

main()