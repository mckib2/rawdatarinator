#!/usr/bin/env python
from rawdatarinator.infoparser import InfoParser
from rawdatarinator.decode_opts import decode_simple_opts
import xml.etree.ElementTree as ET
import re, os, sys
import numpy as np
import h5py

def get_val_by_text(root,search):
    """From MeasYaps XML root find next sibling of node matching 'search'.

    MeasYaps looks like:
    <value>Key</value>
    <value>Value</value>
    Thus 'search' is the Key and we want to find the node that has the Value.
    We return the node containing the desired Value.

    Arguments:
    root            (Element) root XML node (xml.etree.ElementTree Element)

    search          (String) String to match Element.text
    """

    found_flag = False
    for el in root.iter():
        if found_flag:
            return(el)
        if el.text == search:
            # We want the next el
            found_flag = True

def get_yaps_by_name(root,name,afun=lambda x:x,default=None):
    """From XML root, return value of node matching attribute 'name'.

    Arguments:
    root            (Element) Root XML node (xml.etree.ElementTree Element).
                    This is the root of the entire XML document, not the YAPS
                    subtree.

    name            (String) name='name' attribute of ParamLong tag to be
                    matched.

    afun            Anonymous function in the form of a lambda expression to
                    process the string value. Defaults to the identity function.

    default         Default value if node is not found. Defaults to 'None'.
    """

    node = root.find("ParamMap[@name='YAPS']/ParamLong[@name='%s']/value" % name)
    if node is not None:
        return(afun(node.text))
    else:
        return(default)


def readMeasDataVB15(filename,
                     resetFFTscale=False,
                     readOneCoil=False,
                     readPhaseCorInfo=False,
                     readNavigator=False,
                     readTimeStamp=True,
                     nNavEK=False,
                     removeOS=False,
                     removeOSafter=False,
                     transformToImageSpace=False,
                     writeToFile=False,
                     npz=False):
    """Read raw data from Siemens MRI scanners with IDEA VB15.

    Will return an array of measured k-space data from raw data from
    Siemens MRI scanners using IDEA VB15 (single value). If the option
    '-I' is used, then image space data will be returned instead.

    Usage:
    readMeasDataVB15 filename [ -t ] [ -rfft ] [ -r1 ] [ -rp ] [ -rn ]
                              [ -skipts ] [ -nnavek ] [ -ros ]
                              [ -rosa ] [ -I ] [ -w ] [-npz]

    Example:
    readMeasDataVB15 raw.dat -w

    Command-line Options:
    filename        Filename of file containing raw measurements.

    -rfft (resetFFTscale)
                    Resets FFTscale and DataCorrection for each coil
                    to 1.

    -r1 (readOneCoil)
                    Read measurement data from from individual coil.

    -rp (readPhaseCorInfo)
                    _

    -rn (readNavigator)
                    _

    -skipts (skip readTimeStamp)
                    _

    -nnavek (nNavEK)
                    _

    -ros (removeOS)
                    Flag to remove oversampling (OS) in the x
                    direction. removeOS=True is more efficient as it
                    processes each readout line independently,
                    reducing the required memory space to keep all
                    measured data.

    -rosa (removeOSafter)
                    Flag to remove oversampling (OS) in the x
                    direction. This works in image space, cutting FOV.
                    Not likely a good idea for radial.

    -I (transformToImageSpace)
                    Produce image space representation. Note that
                    there is no correction for partial Fourier or
                    parallel imaging k-space undersampling.  The given
                    version of code only uses numpy's FFT operation.

    -w (writeToFile)
                    Save k-space or image space volume. Currently the
                    output filename is auto generated.

    -npz (npz)
                    Save k-space or image space volume using the .npz
                    file extension.  Default is to use hdf5 file
                    standard.

    -h (help)
                    Displays this documentation.
    """

    filename_temp = os.path.splitext(filename)[0]
    if transformToImageSpace is False:
        filenameOut = '%s_Kspace' % filename_temp
    else:
        filenameOut = '%s_imageSpace' % filename_temp

    # Useful Parameters
    globalHeader = 32
    localHeader = 128

    infoParser = InfoParser()
    xmlstr = infoParser.raw2xml(filename)

    # Start in MeasYaps. MeasYaps starts with <value mod="MeasYaps"> and ends at
    # the next XProtocol mod='Phoenix'
    startIdx = xmlstr.find('<value mod="MeasYaps">')
    endIdx = xmlstr.find('<XProtocol mod="Phoenix">')
    my_xmlstr = '<MeasYaps>' + xmlstr[startIdx:endIdx] + '</MeasYaps>' # add root

    # Parse into XML
    root = ET.fromstring(my_xmlstr)

    # Used to decode Partial Fourier fractions (poor man's switch)
    fractionDict = { 10: 1.0,
                     8 : 7./8.,
                     4 : 0.75,
                     2 : 5./8.,
                     1 : 0.5  }

    # vals are tuples: (key,search,default,lambda)
    #     key => key to the dictionary entry
    #     search  => string to search the xml document with
    #     default => if not found in xml doc, use this value
    #     lambda  => whatever value you end up with, operate on it with this
    #                anonymous function.
    vals = [
        ('ScanDimension','sKSpace.ucDimension',None,lambda x:int(x,16)),
        ('flag3D',None,None,lambda _:True if data['ScanDimension'] is 4 else False),
        ('NxAll','sKSpace.lBaseResolution',None,lambda x:int(x)),
        ('NyAll','sKSpace.lPhaseEncodingLines',None,lambda x:int(x)),
        ('OSfactorPE','sKSpace.dPhaseOversamplingForDialog',None,lambda x:1.0 if my_xmlstr.find('sKSpace.dPhaseOversamplingForDialog') < 0 else 1.0+float(x)),
        ('NzAll','sKSpace.lPartitions',None,lambda x:int(x)),
        ('OSfactor3D','sKSpace.dSliceOversamplingForDialog',None,lambda x:1.0 if my_xmlstr.find('sKSpace.dSliceOversamplingForDialog') < 0 else 1.0+float(x)),
        ('phaseResolution','sKSpace.dPhaseResolution',None,lambda x:float(x)),
        ('sliceResolution','sKSpace.dSliceResolution',None,lambda x:float(x)),
        ('Nsl','sSliceArray.lSize',None,lambda x:int(x)),
        ('Nconc','sSliceArray.lConc',None,lambda x:int(x)),
        ('Nc',None,None,lambda _:len(re.findall(r'\.lRxChannelConnected',my_xmlstr))),
        ('Nc',None,None,lambda _:data['Nc']-1 if my_xmlstr.find('AdjustSeq%/AdjCoilSensSeq') > 0 else data['Nc']),
        ('nContrast','lContrasts',1,lambda x:int(x)),
        ('nSet','lSets',1,lambda x:int(x)),
        ('nAverage','lAverages',1,lambda x:int(x)),
        ('nRepetition','lRepetitions',None,lambda x:1 if my_xmlstr.find('lRepetitions') < 0 else 1+int(x)),
        ('nPhase','sPhysioImaging.lPhases',1,lambda x:int(x)),
        ('fractionY','sKSpace.PhasePartialFourier',10,lambda x: fractionDict[int(x)]),
        ('fractionZ','sKSpace.SlicePartialFourier',10,lambda x: fractionDict[int(x)]),
        ('phasePartialFourierForSNR','sKSpace.dSeqPhasePartialFourierForSNR',1.0,lambda x:float(x)),
        ('EPIFactor','sFastImaging.lEPIFactor',None,lambda x:int(x)),
        ('turboFactor','sFastImaging.lTurboFactor',1,lambda x:int(x)),
        ('PATMode','sPat.ucPATMode',None,lambda x:int(x,16)),
        ('PATRefScanMode','sPat.ucRefScanMode',None,lambda x:int(x,16)),
        ('AccelFactorPE','sPat.lAccelFactPE',None,lambda x:int(x)),
        ('AccelFactor3D','sPat.lAccelFact3D',None,lambda x:int(x)),
        ('nRefLinesPE','sPat.lRefLinesPE',None,lambda x:0 if data['AccelFactorPE'] is 1 else int(x)),
        ('nRefLines3D','sPat.lRefLines3D',None,lambda x:0 if data['AccelFactor3D'] is 1 else int(x)) ]

    # Evaluate all tuples
    data = dict() # dictionary to store all values we want to compre with MATLAB
    for tup in vals:
        if tup[1] is not None:
            idx = my_xmlstr.find(tup[1])
        else:
            idx = -1

        if idx < 0:
            val = tup[2] # Take the default if we can't find it
        else:
            val = get_val_by_text(root,tup[1]).text

        afun = tup[3]
        if afun is not None:
            val = afun(val) # Evaluate anonymous function if provided
        data[tup[0]] = val # Store the value in the dictionary

    ## Now use the whole xml document
    root = ET.fromstring(xmlstr)

    # Enforce a max value for Nc
    Nct = get_yaps_by_name(root,'iMaxNoOfRxChannels',lambda x:int(x))
    if Nct is not None:
        data['Nct'] = Nct
        if Nct < data['Nc']:
            data['Nc'] = Nct

    # If this exists, then we'll need it
    nPhCorrScan = get_yaps_by_name(root,'lNoOfPhaseCorrScans',lambda x:int(x))
    if nPhCorrScan is not None:
        data['nPhCorrScan'] = nPhCorrScan

    # Define some more variables
    if data['turboFactor'] > 1:
        data['nPhCorEcho'] = 1
        data['nPhCorScan'] = 1
    if data['EPIFactor'] > 1:
        data['nPhCorScan'] = 1
        data['nPhCorEcho'] = 3

    if data['AccelFactorPE'] is 1:
        data['FirstFourierLine'] = 1
        data['FirstRefLine'] = 1
    else:
        data['FirstFourierLine'] = get_yaps_by_name(root,'lFirstFourierLine',lambda x:1+int(x),1)
        data['FirstRefLine'] = get_yaps_by_name(root,'lFirstRefLine',lambda x:1+int(x),1)

    if data['AccelFactor3D'] is 1:
        data['FirstFourierPar'] = 1
        data['FirstRefPartition'] = 1
    else:
        data['FirstFourierPartition'] = get_yaps_by_name(root,'lFirstFourierPartition',lambda x:1+int(x),1)
        data['FirstRefPartition'] = get_yaps_by_name(root,'lFirstRefPartition',lambda x:1+int(x),1)

    data['NxOS'] = get_yaps_by_name(root,'iNoOfFourierColumns',lambda x:int(x))
    data['OSfactorRO'] = 2 # we can actually find this in YAPS, but MATLAB impl gives as magic num
    data['Nx'] = int(np.around(data['NxOS']/data['OSfactorRO']))
    data['Ny'] = int(root.find("ParamFunctor[@name='FillMiniHeaderData']/ParamLong[@name='NoOfFourierLines']/value").text)
    data['Nz'] = get_yaps_by_name(root,'iNoOfFourierPartitions',lambda x:int(x))
    data['NxRecon'] = get_yaps_by_name(root,'iRoFTLength',lambda x:int(x))
    data['NyRecon'] = get_yaps_by_name(root,'iPEFTLength',lambda x:int(x))
    data['NzRecon'] = 1 if data['Nz'] is 1 else get_yaps_by_name(root,'i3DFTLength',lambda x:int(x))
    data['NslicePerConcat'] = get_yaps_by_name(root,'ushSlicePerConcat',lambda x:int(x))

    ## Partial Fourier Mode and Parameters
    data['PCAlgorithm'] = get_yaps_by_name(root,'lPCAlgorithm',lambda x:int(x))
    data['NoOfPhaseCorrColumns'] = get_yaps_by_name(root,'lNoOfPhaseCorrColumns',lambda x:int(x),data['Nx']/2)
    data['NoOfPhaseCorrLines'] = get_yaps_by_name(root,'lNoOfPhaseCorrLines',lambda x:int(x),data['NyAll']/2)
    data['NoOfPhaseCorrPartitions'] = get_yaps_by_name(root,'lNoOfPhaseCorrPartitions',lambda x:int(x),data['NzAll']/2)
    data['ColSlopeLength'] = get_yaps_by_name(root,'lColSlopeLength',lambda x:int(x),data['Nx']/4)
    # I think there's a mistake here in the MATLAB code: ColSlopeLength defined again instead of LinSlopeLength.
    # Commented is it how I think it should be and we'll go from there. The value is not actually used.
    # data['LinSlopeLength'] = get_yaps_by_name(root,'lLinSlopeLength',lambda x:int(x),data['NyAll']/4)
    data['ColSlopeLength'] = get_yaps_by_name(root,'lLinSlopeLength',lambda x:int(x),data['NyAll']/4)
    data['ParSlopeLength'] = get_yaps_by_name(root,'lParSlopeLength',lambda x:int(x),data['NzAll']/4)

    ## Raw data correction factors, use the MeasYaps portion of the xml document
    root = ET.fromstring(my_xmlstr)
    data['CorrFactor'] = np.ones(data['Nc'])
    for c in range(data['Nc']):
        text = 'axRawDataCorrectionFactor[0][%d].dRe' % c
        data['CorrFactor'][c] = 1 if my_xmlstr.find(text) < 0 else float(get_val_by_text(root,text).text)

        text = 'axRawDataCorrectionFactor[0][%d].dIm' % c
        if my_xmlstr.find(text) >= 0:
            data['CorrFactor'][c] = data['CorrFactor'][c] + 1j*float(get_val_by_text(root,text).text)

    ## FFT Correction Factors
    data['FFTCorrFactor'] = np.ones(data['Nc'])
    if resetFFTscale is False:
        data['FFTCorrFactor'] = np.ones(data['Nc'])
        for c in range(data['Nc']):
            text = 'asCoilSelectMeas[0].aFFT_SCALE[%d].flFactor' % c
            data['FFTCorrFactor'][c] = float(get_val_by_text(root,text).text)

    ## For PC Angio
    data['Nset'] = 1
    text = 'sAngio.ucPCFlowMode'
    data['PCMRAFlag'] = int(get_val_by_text(root,text).text,16) if my_xmlstr.find(text) > 0 else 0

    if data['PCMRAFlag'] is 1:
        text = 'sAngio.sFlowArray.lSize'
        if my_xmlstr.find(text) < 0:
            data['Nset'] = int(get_val_by_text(root,text).text)

    ## Recalculation of partial Fourier factors and EPI/turbo factor for EPI and TSE
    data['fractionPE'] = float(data['Ny'])/float(data['NyAll'])
    data['fraction3D'] = float(data['Nz'])/float(data['NzAll'])
    data['EPIFactor'] = np.around(data['fractionPE']*data['EPIFactor'])
    data['nEPITrain'] = data['Ny']/data['EPIFactor']
    data['turboFactor'] = np.around(data['fractionPE']*data['turboFactor'])
    data['nTSETrain'] = data['Ny']/data['turboFactor']
    data['Nc0'] = data['Nc']
    data['Nc'] = 1 if readOneCoil is True else data['Nc0']

    ## Calculation of the number of valid k-space readouts and k-space data matrix dimensions
    if data['PATMode'] is 1:
        data['nReadout'] = (
            data['nAverage']*    \
            data['nPhase']*      \
            data['nRepetition']* \
            data['nContrast']*   \
            data['Nsl']*         \
            data['Nz']*          \
            data['Nc']*          \
            data['Ny'])

    elif (data['PATMode'] is 2) and (data['PATRefScanMode'] is 2):
        if (data['Ny'] % 2) is 1:
            data['NyPAT'] = (data['Ny'] - 1 + data['nRefLinesPE']*(data['AccelFactorPE'] - 1))/data['AccelFactorPE']
        else:
            data['NyPAT'] = np.floor((data['Ny'] + data['nRefLinesPE']*(data['AccelFactorPE'] - 1))/data['AccelFactorPE'])

        data['nReadout'] = (
            data['nAverage']*    \
            data['nPhase']*      \
            data['nRepetition']* \
            data['nContrast']*   \
            data['Nsl']*         \
            data['Nz']*          \
            data['Nc']*          \
            data['NyPAT'])

    if removeOS is True:
        data['kSpace'] = np.zeros((
            data['nAverage'],
            data['nPhase'],
            data['nRepetition'],
            data['nContrast'],
            data['Nsl'],
            data['Nc'],
            data['Nz'],
            data['Nx'],
            data['Ny']), dtype=np.complex64)
    else:
        data['kSpace'] = np.zeros((
            data['nAverage'],
            data['nPhase'],
            data['nRepetition'],
            data['nContrast'],
            data['Nsl'],
            data['Nc'],
            data['Nz'],
            data['NxOS'],
            data['Ny']), dtype=np.complex64)

    if (readPhaseCorInfo is True) and (data['nPhCorScan'] > 0):
        data['kPhaseCor'] = np.zeros((
            data['nPhCorScan'],
            data['nPhCorEcho'],
            data['Nsl'],
            data['nRepetition'],
            data['Nc'],
            data['NxOS']), dtype=np.float32)

    if readNavigator is True:
        data['nNavigator'] = (
            data['nAverage']*    \
            data['nPhase']*      \
            data['nRepetition']* \
            data['nContrast']*   \
            data['Nsl']*         \
            data['Nz']*          \
            data['Nc']*          \
            data['nEPITrain']    \
            *data['nNavEK'])

        data['kNavigator'] = np.zeros((
            data['nAverage'],
            data['nPhase'],
            data['nRepetition'],
            data['nContrast']*nNavEK,
            data['Nsl'],
            data['Nc'],
            data['Nz'],
            data['nEPITrain'],
            data['NxOS']), dtype=np.float32)

    if readTimeStamp is True:
        data['nTimeStamp'] = (
            data['nAverage']*    \
            data['nPhase']*      \
            data['nRepetition']* \
            data['nContrast']*   \
            data['Nz'])

        data['timeStamp'] = np.zeros((
            data['nAverage'],
            data['nPhase'],
            data['nRepetition'],
            data['nContrast']*nNavEK,
            data['Nz']), dtype=np.float32)

    ## Data Readout and Reordering
    # Read k-space data
    data['noiseMeasCounter'] = 0
    data['noiseMeas'] = np.zeros((data['NxOS'],data['Nc']),dtype=np.complex64)
    data['navigatorPrep'] = 0
    data['LineN'] = -1
    data['Ndr'] = 1

    for r in range(data['Ndr']):
        data['xCoil'] = r
        with open(filename,'rb') as f:
            readFlag = True
            skipField = 0
            countNavigator = 0
            navigatorDataON = False

            temp1 = np.zeros(data['NxOS'])
            data['dataField'] = np.fromfile(f,dtype=np.int32,count=1)[0]
            f.seek(data['dataField'],os.SEEK_SET)

            while readFlag is True:
                if readTimeStamp is True:
                    f.seek(12,os.SEEK_CUR)
                    data['timeS'] = np.fromfile(f,dtype=np.uint32,count=1)[0]
                    f.seek(4,os.SEEK_CUR)
                else:
                    f.seek(20,os.SEEK_CUR)

                data['evalMask1'] = np.fromfile(f,dtype=np.uint32,count=1)[0]
                data['evalMask2'] = np.fromfile(f,dtype=np.uint32,count=1)[0]
                flag = [(32 - m.start()) for m in re.finditer('1',np.binary_repr(data['evalMask1'],32))]

                # Tuples: (key,dtype,afun)
                vals = [ ('Nxr',None,None),
                         ('Ncr',None,None),
                         ('Line',None,None),
                         ('Acquisition',None,None),
                         ('Slice',None,None),
                         ('Partition',None,None),
                         ('Echo',None,None),
                         ('Phase',None,None),
                         ('Repetition',None,None),
                         ('Set',None,None),
                         ('CutOffDataPre',None,lambda:f.seek(12,os.SEEK_CUR)),
                         ('CutOffDataPost',None,None),
                         ('KSpaceCentreColumn',None,None),
                         ('CoilMode',None,None),
                         ('ReadOutOffCentre',np.float32,None),
                         ('KSpaceCentreLineNo',None,lambda:f.seek(4,os.SEEK_CUR)),
                         ('KSpaceCentrePartitionNo',None,None),
                         ('Channel',None,lambda:f.seek(44,os.SEEK_CUR)) ]
                for tup in vals:
                    t = np.uint16 if tup[1] is None else tup[1]
                    if hasattr(tup[2], '__call__'):
                        tup[2]()
                    data[tup[0]] = np.fromfile(f,dtype=t,count=1)[0]

                f.seek(2,os.SEEK_CUR)

                if 1 in flag:
                    break

                if any([k for k in [2,22,26] if k in flag]):
                    if (22 in flag) and (readPhaseCorInfo is False):
                        skipField = data['nPhCorScan']*data['nPhCorEcho']*data['Ncr']*(localHeader + 8*data['Nxr']) - localHeader

                    if (22 in flag) and (readPhaseCorInfo is True):
                        skipField = -localHeader
                        f.seek(skipField,os.SEEK_CUR)
                        skipField = 0

                        for m in range(data['nPhCorScan']*data['nPhCorEcho']*data['Ncr']):
                            infoMDH_TimeStamp = readMDH_TimeStamp_VB13(f)
                            temp = np.fromfile(f,dtype=np.float32,count=2*data['Nxr'])

                            if 25 in flag:
                                temp[0::2] = np.flipud(temp[0::2])
                                temp[1::2] = np.flipud(temp[1::2])
                            if data['CutOffDataPre'] > 0:
                                temp[0:2*data['CutOffDataPre']] = 0
                            if data['CutOffDataPost'] > 0:
                                temp[len(temp) - 2*data['CutOffDataPost']:] = 0

                            data['kPhaseCor'][data['Echo'],np.ceil(m/data['Ncr']),data['Slice'],data['Repetition'],data['Channel'],:] = (temp[0::2] + 1j*temp[1::2]).astype(np.float32)

                    if (2 in flag) and (readNavigator is False):
                        skipField = data['Ncr']*(localHeader + 8*data['Nxr']) - localHeader
                    if (2 in flag) and (readNavigator is True):
                        if (countNavigator is False) and (navigatorPrep is False):
                            kNavigator = np.zeros((
                                data['Nxr'],
                                data['Ncr'],
                                data['nContrast']*nNavEK,
                                data['nEPITrain'],
                                data['Nz'],
                                data['Nsl'],
                                data['nAverage'],
                                data['nPhase'],
                                data['nRepetition']),dtype=np.float32)
                            kNavigatorTemp = np.zeros((
                                data['Nxr'],
                                data['Ncr'],
                                data['nContrast']*nNavEK),dtype=float32)
                            navigatorPrep = 1

                        skipField = -localHeader
                        f.seek(skipField,os.SEEK_CUR)
                        skipField = 0

                        for m in range(nNavEK*data['Ncr']):
                            infoMDH_TimeStamp = readMDH_TimeStamp_VB13(f)
                            temp = np.fromfile(f,dtype=np.float32,count=2*data['Nxr'])

                            if 25 in flag:
                                temp[0::2] = np.flipud(temp[0::2])
                                temp[1::2] = np.flipud(temp[1::2])
                            if data['CutOffDataPre'] > 0:
                                temp[0:2*data['CutOffDataPre']] = 0
                            if data['CutOffDataPost'] > 0:
                                temp[len(temp) - 2*data['CutOffDataPost']-1:] = 0;
                            kNavigatorTemp[:,data['Channel'],data['Echo']] = (temp[0::2] + 1j*temp[1::2]).astype(np.complex64)

                        navigatorDataON = True

                    if 26 in flag:
                        temp = np.fromfile(f,dtype=np.float32,count=2*data['Nxr'])

                        if 25 in flag:
                            temp[0::2] = np.flipud(temp[0::2])
                            temp[1::2] = np.flipud(temp[1::2])

                        data['noiseMeas'][:,data['Channel']] = temp[0::2] + 1j*temp[1::2]
                        skipField = 0

                    f.seek(skipField,os.SEEK_CUR)

                else:
                    temp = np.fromfile(f,dtype=np.float32,count=2*data['Nxr'])
                    if 25 in flag:
                        temp[0::2] = np.flipud(temp[0::2])
                        temp[1::2] = np.flipud(temp[1::2])
                    if data['CutOffDataPre'] > 0:
                        temp[0:2*data['CutOffDataPre']-1] = 0
                    if data['CutOffDataPost'] > 0:
                        temp[len(temp) - 2*data['CutOffDataPost']-1] = 0
                    if 11 in flag:
                        temp = data['CorrFactor'][data['Channel']]*temp
                    temp = data['FFTCorrFactor'][data['Channel']]*temp

                    if readOneCoil is False:
                        if removeOS is True:
                            temp1[len(temp1) - data['Nxr']:] = temp[0::2] + 1j*temp[1::2]
                            tempX = np.fftshift(np.fft(np.fftshift(temp1)))
                            tempK = np.fftshift(np.ifftshift(np.fftshift(tempX[np.around((data['NxOS'] - data['Nx'])/2):data['Nx'] + np.around((data['NxOS'] - data['Nx'])/2)])))
                            data['kSpace'][data['Acquisition'],data['Phase'],data['Repetition'],data['Echo'],data['Slice'],data['Channel'],data['Partition'],:,data['Line']] = tempK.astype(np.complex64)
                        else:
                            data['kSpace'][data['Acquisition'],data['Phase'],data['Repetition'],data['Echo'],data['Slice'],data['Channel'],data['Partition'],data['kSpace'].shape[7] - data['Nxr']:data['kSpace'].shape[7],data['Line']] = (temp[0::2] + 1j*temp[1::2]).astype(np.complex64)

                    elif (readOneCoil is True) and (data['Channel']+1 == coilIndex):
                        if removeOS is True:
                            temp1[len(temp1) - data['Nxr']:] = temp[0::2] + 1j*temp[1::2]
                            tempx = np.fftshift(np.fft(np.fftshift(temp1)))
                            tempK = np.fftshift(np.fft(np.fftshift(tempX[np.around((data['NxOS'] - data['Nx'])/2):data['Nx'] + np.around((data['NxOS'] - data['Nx'])/2)])))
                            data['kSpace'][data['Acquisition'],data['Phase'],data['Repetition'],data['Echo'],data['Slice'],0,data['Partition'],:,data['Line']] = tempK.astype(np.complex64)
                        else:
                            data['kSpace'][data['Acquisition'],data['Phase'],data['Repetition'],data['Echo'],data['Slice'],0,data['Partition'],data['kSpace'].shape[7] - data['Nxr']:,data['Line']] = (temp[0::2] + 1j*temp[1::2]).astype(np.complex64)

                    if (readTimeStamp is True) and (data['Channel'] == 0) and (navigatorDataON is True):
                        data['EPITrain'] = countNavigator % data['nEPITrain']
                        data['timeStamp'][data['Echo'],data['EPITrain'],data['Partition'],data['Slice'],data['Acquisition'],data['Phase'],data['Repetition']] = (0.0025*timeS).astype(np.complex64)

                    if (readNavigator is True) and (data['Channel'] == 0) and (navigatorDataON is True):
                        data['EPITrain'] = countNavigator % data['nEPITrain']
                        kNavigator[:,:,:,data['EPITrain'],data['Partition'],data['Slice'],data['Acquisition'],data['Phase'],data[Repetition]] = kNavigatorTemp.astype(np.complex64)
                        navigatorDataON = False
                        countNavigator += 1

                if 1 in flag:
                    break

    data['kSpace'] = np.squeeze(data['kSpace'])

    if len(data['kSpace'].shape) == 3:
        data['kSpace'] = np.transpose(data['kSpace'],[1,2,0])
    elif len(data['kSpace'].shape) == 4:
        if data['flag3D'] is False:
            data['kSpace'] = np.transpose(data['kSpace'],[2,3,0,1])
        else:
            data['kSpace'] = np.transpose(data['kSpace'],[2,3,1,0])
    elif len(data['kSpace'].shape) == 5:
        data['kSpace'] = np.transpose(data['kSpace'],[3,4,2,0,1])

    if transformToImageSpace is True:
        if data['flag3D'] is True:
            data['imSpace'] = np.fft.ifftshift(np.fft.ifftn(np.fft.fftshift(data['kSpace'],axes=(0,1,2)),axes=(0,1,2)),axes=(0,1,2))
            data['imSpace'][2] *= data['Nz']
        else:
            data['imSpace'] = np.fft.ifftshift(np.fft.ifft2(np.fft.fftshift(data['kSpace'],axes=(0,1)),axes=(0,1)),axes=(0,1))

        data['imSpace'][0] *= data['NxOS']
        data['imSpace'][1] *= data['Ny']

        if (removeOSafter is True) and (removeOS is False):
            if len(data['imSpace'].shape) == 2:
                data['imSpace'][0:data['NxOS']/4,:] = []
                data['imSpace'][data['imSpace'].shape[0] - data['NxOS']/4 :,:] = []
            elif len(data['imSpace'].shape) == 3:
                data['imSpace'][0:data['NxOS']/4,:,:] = []
                data['imSpace'][data['imSpace'].shape[0] - data['NxOS']/4:,:,:] = []
            elif len(data['imSpace'].shape) == 4:
                data['imSpace'][0:data['NxOS']/4,:,:,:] = []
                data['imSpace'][data['imSpace'].shape[0] - data['NxOS']/4:,:,:,:] = []
            elif len(data['imSpace'].shape) == 5:
                data['imSpace'][0:data['NxOS']/4,:,:,:,:] = []
                data['imSpace'][data['imSpace'].shape[0] - data['NxOS']/4:,:,:,:,:] = []

    if writeToFile is True:
        if transformToImageSpace is True:
            if npz:
                np.savez_compressed(filenameOut,imSpace=data['imSpace'],timeStamp=data['timeStamp'])
            else:
                with h5py.File('%s.hdf5' % filenameOut,'w') as f:
                    dset = f.create_dataset('kSpace',data=data['imSpace'])
        else:
            if npz:
                np.savez_compressed(filenameOut,kSpace=data['kSpace'],timeStamp=data['timeStamp'])
            else:
                with h5py.File('%s.hdf5' % filenameOut,'w') as f:
                    dset = f.create_dataset('kSpace',data=data['kSpace'])

    return(data)

if __name__ == '__main__':

    options = { '-rfft':   ['resetFFTscale',False],
                '-r1':     ['readOneCoil',False],
                '-rp':     ['readPhaseCorInfo',False],
                '-rn':     ['readNavigator',False],
                '-skipts': ['readTimeStamp',True],
                '-nnavek': ['nNavEK',False],
                '-ros':    ['removeOS',False],
                '-rosa':   ['removeOSafter',False],
                '-I':      ['transformToImageSpace',False],
                '-w':      ['writeToFile',False],
                '-npz':    ['npz',False] }

    decode_simple_opts(options,sys.argv[1:],readMeasDataVB15)
