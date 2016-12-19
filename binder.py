#===============================================================================
# Robert Mitchell
# Computer Science - CSUF
#
# Binder Script.
# This python script reads a variable number of execuable files, writing them
# sequentially into a 2d char array in a C++ header file. The header is then
# compiled with 'binderbackend.cpp' as a single executable. binderbackend.cpp
# is responsible for reading the bytes of the executables array from the header
# and forking a process for each executable in the array.
#
# Intended for use on linux.
#===============================================================================

import os
import sys
from subprocess import call
import os
from subprocess import Popen, PIPE

#===============================================================================

# The file name of the header file we are building that contains our byterized executables.
HEADER_NAME = 'codearray.h'

# The file name of the binder source.
SOURCE_NAME = 'binderbackend.cpp'

# The output's name.
EXEC_NAME = 'bound'

#===============================================================================
# Returns the hexidecimal dump of a particular binary file
# @execPath - the executable path
# @return - returns the hexidecimal string representing
# the bytes of the program. The string has format:
# byte1,byte2,byte3....byten,
# For example, 0x19,0x12,0x45,0xda,
#===============================================================================
def getHexDump(execPath):
	# open file to read.
	exe = open(execPath, "rb")
	# string to store hexdump.
	execBytes = ''
	while True:
	    byte = exe.read(1)
	    if len(byte) == 0:
	        break
	    execBytes += '0x'+str(byte.encode('hex')) #store the byte
	    execBytes += ',' # put a comma after it. i.e. format for C++ array syntax.
	# close the file.
	exe.close()

	return execBytes[:-1]

#===============================================================================
# Generates the header file containing an array of executable codes
# @param execList - the list of executables
# @param fileName - the header file to which to write data
#===============================================================================
def generateHeaderFile(execList, fileName):
	# print status.
	print 'writing header'

	# The header file
	headerFile = None

	# Open the header file
	headerFile = open(fileName, "w")

	# The lengths of programs
	progLens = []

	# The number of program names to write.
	numProgs = len(execList)

	# Write libraries and namespace statements to header file.
	headerFile.write('#include <string>\n\nusing namespace std;')

	# For each program progName we should run getHexDump() and get the
	# the string of bytes formatted according to C++ conventions. That is, each
	# byte of the program will be a two-digit hexadecimal value prefixed with 0x.
	# For example, 0xab. Each such byte should be added to the array codeArray in
	# the C++ header file. After this loop executes, the header file should contain
	# an array of the following format:
	#
	# format to store executable bytes as valid C++ arrays:
	# unsigned char* codeArray[] = { new unsigned char[progLen0] { 0xff, 0xab, ...}, new unsigned char[progLen1] {...} ... };
	#
	# example : unsigned char* codeArray[] = {new unsigned char[3]{0xab,0xab,0xab}, new unsigned char[2]{0xac, 0xff}};

	# write a dynamic array of pointers to the hearder file that will be declared on the heap.
	headerFile.write('\n\nunsigned char* codeArray[] = {')

	# Write the C++ formatted Hexadecimal data to the header file for each executable name in the list.
	for i, progName in enumerate(execList):

		# print status
		print 'reading execuable bytes: ' + str(i) + ' : ' + progName

		# get C++ formatted hex string for program.
		progHex = getHexDump(progName)

		# if the hex dump is good, write it to the header file and update prog variables.
		if progHex != None:
			# get length. Is there better way to do this? Hmmm. At least this solution is only one line.
			progLen = progHex.count('0x')

			# save the length (in bytes) of the executable.
			progLens.append(progLen)

			headerFile.write('new unsigned char[' + str(progLen) + ']{')

			# write the C++ formated hex data to the header file's array.
			if i == numProgs-1: # if this is the last program to write ...
				# write the comma separated hex values and close the brace without a trailing comma.
				headerFile.write(progHex + '}')
			else:
				# write the comma separated hex values and close the brace WITH a trailing comma.
				headerFile.write(progHex + '},')
		else:
			headerFile.close()
			sys.exit('could not obtain hexdump of executable: ' + progName)

	# close the byte array contain hex data of our executables we wish to hide.
	headerFile.write('};')

	# Add array to containing program lengths to the header file
	headerFile.write("\n\nunsigned int progLens[] = {")

	# Add to the array in the header file the sizes of each program.
	# That is the first element is the size of program 1, the second element
	# is the size of program 2, etc.
	for i, length in enumerate(progLens):
		# write the program lengths to the array in the header file.
		if i == numProgs-1:
			# if we are writing the last one, don't add the trailing comma.
			headerFile.write(str(length))
		else:
			# write the length with the trailing comma.
			headerFile.write(str(length)+',')

	# close the array of program lengths.
	headerFile.write('};')

	# Write the number of programs.
	headerFile.write("\n\n#define NUM_BINARIES " + str(numProgs))

	# Close the header file
	headerFile.close()

	# Print status
	print 'header built: ' + fileName

#===============================================================================
# Compiles the combined binaries
# @param binderCppFileName - the name of the C++ binder file
# @param execName - the executable file name
#===============================================================================
def compileFile(sourceName, execName):

	# print status
	print("compiling...")

	# define G++ compile command for compiling our executable(s) containing header file and our C++ binder file.
	# using gcc to compile produces errors.
	command = 'g++ -std=gnu++11 ' + sourceName + ' -o ' + execName

	# Use Popen() to run G++. Without shell=True, Popen crashes, even though we don't use the shell?
	gppOutput = Popen(command, stdout=PIPE, stderr=None, shell=True)

	# Capture standard output and error streams from PIPE to to subprocess. This makes it blocking.
	stdout, stderr = gppOutput.communicate()

	# report the status of the compilation to the console.
	if stderr == None:
		 print stdout
		 print 'compilation succeeded without errors'
	else:
		sys.exit('compilation failed')

#===============================================================================
# step 1: generate the header file
generateHeaderFile(sys.argv[1:], HEADER_NAME)
# step 2: compile the header file with binder backend
#compileFile(SOURCE_NAME, EXEC_NAME)
#===============================================================================
