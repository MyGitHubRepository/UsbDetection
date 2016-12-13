""" Project: Windows USB Operations Date:30.09.2016 """

#import modules
import win32file
import os
import ntpath #Windows path convention
import shutil
import time
from datetime import datetime
from multiprocessing import Queue

#Global definitions
debug_mode_active = False
quite_mode_active = False
	
#Debug functions
def set_trace_mode(debug_mode, quite_mode):
	global debug_mode_active
	global quite_mode_active
	debug_mode_active = debug_mode
	quite_mode_active = quite_mode

def print_trace(x):
	global debug_mode_active
	global quite_mode_active
	if debug_mode_active and not quite_mode_active:
		print x

def print_trace2(x,y):
	global debug_mode_active
	global quite_mode_active
	if debug_mode_active and not quite_mode_active:
		print x,y

#Utils functions
def get_drive_list():
	drive_list = []
	remote_drive_list = []
	fixed_drive_list = []
	removable_drive_list = []
	ram_drive_list = []
	cd_rom_drive_list = []

	drivebits=win32file.GetLogicalDrives()
	for d in range(1,26):
		mask=1 << d
		if drivebits & mask:
			# here if the drive is at least there
			drname='%c:\\' % chr(ord('A')+d)
			t=win32file.GetDriveType(drname)
			if t == win32file.DRIVE_REMOTE:
				remote_drive_list.append(drname)
			elif t == win32file.DRIVE_FIXED:
				fixed_drive_list.append(drname)
			elif t == win32file.DRIVE_REMOVABLE:
				removable_drive_list.append(drname)
			elif t == win32file.DRIVE_RAMDISK:
				ram_drive_list.append(drname)
			elif t == win32file.DRIVE_CDROM:
				cd_rom_drive_list.append(drname)

	#Add all drives to list
 	drive_list.append(remote_drive_list)
 	drive_list.append(fixed_drive_list)
 	drive_list.append(removable_drive_list)
	drive_list.append(ram_drive_list)
	drive_list.append(cd_rom_drive_list)

	if debug_mode_active:
		switcher = {
			0: "Remote Drive List:",
			1: "Fixed Drive List:",
			2: "Removable Drive List:",
			3: "Ram Drive List:",
			4: "Cd-rom Drive List:",
		}	

		for list_item in range(0, len(drive_list)):
			if len(drive_list[list_item]) > 0:
				print switcher.get(list_item, "nothing")
			for item in range(0, len(drive_list[list_item])):
				print drive_list[list_item][item]
	
	return drive_list
	
def usb_check_file_type_match(args,file_name):
	is_type_matched = True
	if args.type != None:
		if file_name.endswith("."+args.type):
			is_type_matched = True
		else:
			is_type_matched = False
		
		print_trace2("is_type_matched =" ,is_type_matched)
	
	return is_type_matched

def usb_check_file_lower_size_match(args,file_name):	
	is_size_accepted = True
	if args.lowerSize != None:
		if os.path.getsize(file_name) <= int(args.lowerSize):
			is_size_accepted = True
		else:
			is_size_accepted = False
		
		print_trace2("File size is ", os.path.getsize(file_name))
		print_trace2("is_size_accepted = ", is_size_accepted)
	
	return is_size_accepted

def usb_check_file_higher_size_match(args,file_name):	
	is_size_accepted = True
	if args.higherSize != None:
		if os.path.getsize(file_name) >= int(args.higherSize):
			is_size_accepted = True
		else:
			is_size_accepted = False
		
		print_trace2("File size is ", os.path.getsize(file_name))
		print_trace2("is_size_accepted = ", is_size_accepted)
	
	return is_size_accepted	

def usb_check_file_date_match(args,file_name):	
	is_date_accepted = True
	if (args.dateAfter != None) or (args.dateBefore != None):		
		if args.dateAfter != None:
			date = args.dateAfter.split("/")
			day = date[0]
			month = date[1]
			year = date[2]
			seconds = datetime(int(year), int(month), int(day), 0, 0)
			seconds = (seconds - datetime(1970, 1, 1)).total_seconds()
			print_trace2("File date = ", time.ctime(os.path.getmtime(file_name)))
			if os.path.getmtime(file_name) >= seconds :
				is_date_accepted = True
			else:
				is_date_accepted = False
				print_trace2("is_date_accepted = ", is_date_accepted)
				return is_date_accepted
		
		if args.dateBefore != None:
			date = args.dateBefore.split("/")
			day = date[0]
			month = date[1]
			year = date[2]
			seconds = datetime(int(year), int(month), int(day), 0, 0)
			seconds = (seconds - datetime(1970, 1, 1)).total_seconds()
			print_trace2("File date = ", time.ctime(os.path.getmtime(file_name)))
			if os.path.getmtime(file_name) <= seconds:
				is_date_accepted = True
			else:
				is_date_accepted = False
				print_trace2("is_date_accepted = ", is_date_accepted)
				return is_date_accepted
	
	print_trace2("is_date_accepted = ", is_date_accepted)
	return is_date_accepted

def usb_check_files_path(args):
	file_paths = []
	for root, directories, files in os.walk(args.source):
		for n in files:
			filepath = os.path.join(root, n)
			file_paths.append(filepath)
			print_trace2("file path is = " ,filepath)
	return file_paths	
	
def usb_check_pre_conditions_existence(args):
	pre_condition_exist = False;
	
	if args.type != None:
		pre_condition_exist = True
	elif not pre_condition_exist and args.dateBefore != None:
		pre_condition_exist = True
	elif not pre_condition_exist and args.dateAfter != None:
		pre_condition_exist = True
	elif not pre_condition_exist and args.lowerSize != None:
		pre_condition_exist = True
	elif not pre_condition_exist and args.higherSize != None:
		pre_condition_exist = True
	
	return pre_condition_exist

def usb_check_file_pre_conditions(args,file_name):
	pre_condition_matched = True;
	
	pre_condition_matched = pre_condition_matched and usb_check_file_type_match(args, file_name)
	pre_condition_matched = pre_condition_matched and usb_check_file_lower_size_match(args, file_name)
	pre_condition_matched = pre_condition_matched and usb_check_file_higher_size_match(args, file_name)
	pre_condition_matched = pre_condition_matched and usb_check_file_date_match(args, file_name)

	print_trace2("Precondition status = ", pre_condition_matched)
	return pre_condition_matched

def usb_copy(args):
	source_path = args.source
	destination_path = args.destination
	if source_path != None and destination_path != None:
		if args.all: #Copy all files and directory
			src_files = os.listdir(source_path)
			for file_name in src_files:
				full_file_name = os.path.join(source_path, file_name)
				print_trace2("full file name = " ,full_file_name)
				if (os.path.isfile(full_file_name)):
					if usb_check_file_pre_conditions(args, full_file_name):
						shutil.copyfile(full_file_name, destination_path+file_name)
				elif(os.path.isdir(full_file_name)):
					if usb_check_file_pre_conditions(args, full_file_name):
						shutil.copytree(full_file_name, destination_path+file_name)
		else: #Copy file or directory to destination
			if(os.path.isfile(source_path)):
				file_name = ntpath.basename(source_path)
				print_trace(file_name)
				if usb_check_file_pre_conditions(args, source_path):
					shutil.copyfile(source_path, destination_path+file_name)
			elif(os.path.isdir(source_path)):
				directory = ntpath.basename(source_path)
				print_trace2("directory path = " ,directory)
				if usb_check_file_pre_conditions(args, source_path):
					shutil.copytree(source_path, destination_path+directory)
			else:
				print_trace2("Source can't find src =", source_path)
	else:
		print "Missing destination/source path please use -h for help"