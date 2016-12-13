""" Project: Windows USB Operations Date:30.09.2016 """
import sys
import argparse

from UsbWinUtils import *
		
def parseCmds(argv):
	
	usage = """
	This tool is used for usb automation on windows
	You can start with below usage examples.
	In any bug report, please contact with
	hakan.etik@gmail.com
	"""
	
	parser = argparse.ArgumentParser(usage)
	
	group_op = parser.add_mutually_exclusive_group()
	group_op.add_argument("-s", "--show", help="show available drivers", action="store_true")
	group_op.add_argument("-c", "--copy", help="copy source file to destination", action="store_true")
	group_op.add_argument("-a", "--all", help="copy all files(source is directory) to destination", action="store_true")

	group_debug = parser.add_mutually_exclusive_group()
	group_debug.add_argument("-v", "--verbose", help="open verbose outputs", action="store_true")
	group_debug.add_argument("-q", "--quite", help="quite execution", action="store_true", default=False)

	parser.add_argument("-src", "--source", help="source path")
	parser.add_argument("-d", "--destination", help="destination path")
	parser.add_argument("-t", "--type", help="determine type of file/files")
	parser.add_argument("-ls", "--lowerSize", help="determine lower size limitation of file/files")
	parser.add_argument("-hs", "--higherSize", help="determine higher size limitation of file/files")
	parser.add_argument("-da", "--dateAfter", help="get file/files after this date(D/M/Y)")
	parser.add_argument("-db", "--dateBefore", help="get file/files before this date(D/M/Y)")
	
	args = parser.parse_args()
	
	set_trace_mode(args.verbose,args.quite)

	print_trace2("Source path: ", args.source)
	print_trace2("Destination path: ", args.destination)
					
	return args

def processCmds(args):
	if args.show: #Show mounted drivers
		get_drive_list()
	elif args.copy or args.all: #Process copy command
		usb_copy(args)
			
def main(argv):

	if len(argv) == 1:
		print "Please use --help or -h for proper usage"
	else:
		args = parseCmds(argv)
		processCmds(args)

if __name__=='__main__':
	main(sys.argv)