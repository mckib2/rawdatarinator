# Python port of program to read measurement data
# from Siemens MRI scanners with IDEA VB15.
# Originally written in MATLAB.

# Version 1.0
# AUTHOR of MATLAB implementation: Eugene G. Kholmovski, PhD
# UCAIR, Department of Radiology, University of Utah
# ekhoumov@ucair.med.utah.edu

# Python port: Nicholas McKibben, Bangerter Research Group BYU

import numpy as np

def readMeasDataVB15(filename):
	globalHeader = 32
	localHeader = 128

	# Read protocol from filename.dat file
	with open(filename,'r') as f:
		fileData = np.fromfile(f,dtype=np.int32)
		# dataField = np.fromfile(f,dtype=np.int32)[0]
		# info = np.fromfile(f,dtype=np.intc)
		# dataField = int.from_bytes(f.read(1), byteorder='little')

	print(dataField)
	print(dataField.shape)
	print(info)

	# print("fid: ",fid)

	# dataField = fread(fid,1,'int32')
	# print("dataField: ",dataField)
	# info = fread(fid,dataField - 4,'uchar')
	# print("info: ",info)
	# info = char(info)
	# print("info: ",info)
	# fclose(fid)
	# longProtocol = info
	# print("longProtocol: ",longProtocol)


readMeasDataVB15('test.dat')
