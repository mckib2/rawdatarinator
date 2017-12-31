# Python port of program to read measurement data
# from Siemens MRI scanners with IDEA VB15.
# Originally written in MATLAB.

# Version 1.0
# AUTHOR of MATLAB implementation: Eugene G. Kholmovski, PhD
# UCAIR, Department of Radiology, University of Utah
# ekhoumov@ucair.med.utah.edu
# Python port: Nicholas McKibben, Bangerter Research Group BYU

import numpy as np
import re

def readMeasDataVB15(filename):
	globalHeader = 32
	localHeader = 128

	# Read protocol from filename.dat file
	with open(filename,'r') as f:
                dataField = np.fromfile(f,dtype=np.int32,count=1)
                info = f.read(dataField-4);
        longProtocol = info

        # Now get a substring embedded in the long protocol
        startWord = "MeasYaps"
        startIdx = info.find(startWord) + len(startWord) + 5
        endWord = "Phoenix"
        endIdx = info.find(endWord,startIdx)
        shortProtocol = info[startIdx:endIdx]

        # Switch to the shortProtocol
        info = shortProtocol

        # Some acquisition parameters from filename.asc
        text = "ucDimension                      = 0x"
        t = info.find(text) + len(text)
        ScanDimension = sscanf(info[t:t+10],'%d')
        flag3D = True if ScanDimension is 4 else False

        text = "sKSpace.lBaseResolution                  = "
        t = info.find(text) + len(text)
        NxAll = sscanf(info[t:t+10],'%d')
        
        text = "sKSpace.lPhaseEncodingLines              = "
        t = info.find(text) + len(text)
        NyAll = sscanf(info[t:t+10],'%d')

        text = "sKSpace.dPhaseOversamplingForDialog      = "
        t = info.find(text)
        OSfactorPE = 1 if t is -1 else (1 + sscanf(info[(t+len(text)):(t+len(text))+10],'%f'))

        text = "sKSpace.lPartitions                      = "
        t = info.find(text) + len(text)
        NzAll = sscanf(info[t:t+10],'%d')

        text = "sKSpace.dSliceOversamplingForDialog      = "
        t = info.find(text)
        OSfactor3D = 1 if t is -1 else (1 + sscanf(info[(t+len(text)):(t+len(text))+10],'%f'))

        text = "sKSpace.dPhaseResolution                 = "
        t = info.find(text) + len(text)
        phaseResolution = sscanf(info[t:t+10],'%f')

        text = "sKSpace.dSliceResolution                 = "
        t = info.find(text) + len(text)
        sliceResolution = sscanf(info[t:t+10],'%f')

        text = "sSliceArray.lSize                        = "
        t = info.find(text) + len(text)
        Nsl = sscanf(info[t:t+10],'%d')
        
        text = "sSliceArray.lConc                        = "
        t = info.find(text) + len(text)
        Nconc = sscanf(info[t:t+10],'%d')

        text = ".lRxChannelConnected = "
        t = list(findall(text,info))
        Nc = len(t)

        text = "AdjustSeq%/AdjCoilSensSeq"
        t = info.find(text)
        if t is not -1:
                Nc = Nc - 1

        text = "lContrasts                               = "
        t = info.find(text)
        nContrast = 1 if t is -1 else sscanf(info[(t+len(text)):(t+len(text))+10],'%d')
                
        text = "lSets                                    = "
        t = info.find(text)
        nSet = 1 if t is -1 else sscanf(info[(t+len(text)):(t+len(text))+10],'%d')

        text = "lAverages                                = "
        t = info.find(text)
        nAverage = 1 if t is -1 else sscanf(info[(t+len(text)):(t+len(text))+10],'%d')

        text = "lRepetitions                             = "
        t = info.find(text)
        nRepetition = 1 if t is -1 else (1 + sscanf(info[(t+len(text)):(t+len(text))+10],'%d'))

        text = "sPhysioImaging.lPhases                   = "
        t = info.find(text)
        nPhase = 1 if t is -1 else sscanf(info[(t+len(text)):(t+len(text))+10],'%d')

        text = "sKSpace.PhasePartialFourier            = 0x"
        t = info.find(text)
        fractionFlag = 10 if t is -1 else int(info[(t+len(text)):(t_len(text))+1])

        fractionDict = {
                10: 1.0,
                8 : 7./8.,
                4 : 0.75,
                2 : 5./8.,
                1 : 0.5
        }
        
        fractionY = fractionDict[fractionFlag];

        text = "sKSpace.SlicePartialFourier            = 0x"
        t = info.find(text)
        fractionFlag = 10 if t is -1 else int(info[(t+len(text)):(t_len(text))+1])
        fractionZ = fractionDict[fractionFlag]

        text = "sKSpace.dSeqPhasePartialFourierForSNR    = "
        t = info.find(text)
        phasePartialFourierForSNR = 1.0 if t is -1 else sscanf(info[(t+len(text)):(t+len(text))+10],'%f')

        text = "sFastImaging.lEPIFactor                  = "
        t = info.find(text) + len(text)
        EPIFactor = sscanf(info[t:t+10],'%d')

        text = "sFastImaging.lTurboFactor                = "
        t = info.find(text)
        turboFactor = 1 if t is -1 else sscanf(info[(t+len(text)):(t+len(text))+10],'%d')

        # iPAT paraemters from filename.asc
        text = "sPat.ucPATMode                           = 0x"
        t = info.find(text) + len(text)
        PATMode = sscanf(info[t:t+1],'%d')

        text = "sPat.ucRefScanMode                       = 0x"
        t = info.find(text) + len(text)
        PATRefScanMode = sscanf(info[t:t+1],'%d')

        text = "sPat.lAccelFactPE                        = "
        t = info.find(text) + len(text)
        AccelFactorPE = sscanf(info[t:t+10],'%d')

        text = "sPat.lAccelFact3D                        = "
        t = info.find(text) + len(text)
        AccelFactor3D = sscanf(info[t:t+10],'%d')

        if AccelFactorPE is 1:
                nRefLinesPE = 0
        else:
                text = "sPat.lRefLinesPE                         = "
                t = info.find(text) + len(text)
                nRefLinesPE = sscanf(info[t:t+10],'%d')

        if AccelFactor3D is 1:
                nRefLines3D = 0
        else:
                text = "sPat.lRefLines3D                         = "
                t = info.find(text) + len(text)
                nRefLines3D = sscanf(info[t:t+10],'%d')

        # Change over to the longProtocol
        info = longProtocol
                
        

def sscanf(toparse,specifier):
        # remove indices, as the numbers inside them confuse us
        toparse = re.sub(r'\[(.*)\]','[]',toparse);
        
        val = ''.join([x for x in toparse if x.isdigit() or x is '.' ])
        
        if specifier == '%d':
                val = int(float(val))
        elif specifier == '%f':
                val = float(val)
                
        return(val)

def findall(substring, string):
        last_found = -1
        while True:
                last_found = string.find(substring, last_found + 1)
                if last_found == -1:  
                        break
                yield last_found
                
readMeasDataVB15('test-data/test.dat')
