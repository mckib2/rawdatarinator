from infoparser import raw2xml
import xml.etree.ElementTree as ET
import re
import numpy as np

def get_val_by_text(root,search):
    found_flag = False
    for el in root.iter():
        if found_flag:
            return(el)
        if el.text == search:
            # We want the next el
            found_flag = True

def get_yaps_by_name(root,name,afun=lambda x:x,default=None):
    node = root.find("ParamMap[@name='YAPS']/ParamLong[@name='%s']/value" % name)
    if node is not None:
        return(afun(node.text))
    else:
        return(default)
            
def readMeasDataVB15(filename):
    ### Flags:
    resetFFTscale = False # True => resets FFTscale and DataCorrection for each coil to 1
    readOneCoil = False # True => read Meas Data from Individual Coil
    readPhaseCorInfo = False
    readNavigator = False
    readTimeStamp = True
    nNavEK = False
    
    # Flags to remove oversampling (OS) in x-direction
    # One of these flags should be equal to 1 to remove OS.
    # removeOS=1 is more efficient as it processes each readout line
    # independently reducing the required memory space to keep all measured
    # data.
    removeOS = False
    removeOSafter = False # note this works in image space, cutting FOV. Not likely good idea for radial

    
    xmlstr = raw2xml(filename)

    # Start in MeasYaps:
    # MeasYaps starts with <value mod="MeasYaps">
    # and ends at the next XProtocol, Phoenix
    startIdx = xmlstr.find('<value mod="MeasYaps">')
    endIdx = xmlstr.find('<XProtocol mod="Phoenix">')
    my_xmlstr = '<MeasYaps>' + xmlstr[startIdx:endIdx] + '</MeasYaps>'
    
    # Parse into XML
    root = ET.fromstring(my_xmlstr)

    # Used to decode Partial Fourier fractions
    fractionDict = {
        10: 1.0,
        8 : 7./8.,
        4 : 0.75,
        2 : 5./8.,
        1 : 0.5
    }
    
    # Find the values we need.  Here's the deal...
    # I'm going to be a little cute about it.
    # vals are tuples: (key,search,default,lambda)
    #     key => key to the dictionary entry
    #     search => string to search the xml document with
    #     default => if not found in xml doc, use this value
    #     lambda => whatever value you end up with, operate on
    #               it with this anonymous function.
    vals = [
        ('ScanDimension','sKSpace.ucDimension',None,lambda x:int(x,16)),
        ('flag3D',None,None,lambda _: True if data['ScanDimension'] is 4 else False),
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
    data = dict()
    for tup in vals:
        if tup[1] is not None:
            idx = my_xmlstr.find(tup[1])
        else:
            idx = -1
            
        # Take the default if we can't find it
        if idx < 0:
            val = tup[2]
        else:
            val = get_val_by_text(root,tup[1]).text
            
        # Evaluate anonymous function if provided
        afun = tup[3]
        if afun is not None:
            val = afun(val)

        # Store the value in the dictionary
        #print('Result: %s %s' % (type(val),val))
        data[tup[0]] = val


    ### Adjust various values using the whole xml document
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
    
    # Define some extra variables
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
    data['OSfactorRO'] = 2 # we can actually find this in YAPS
    data['Nx'] = int(np.around(data['NxOS']/data['OSfactorRO']))
    data['Ny'] = int(root.find("ParamFunctor[@name='FillMiniHeaderData']/ParamLong[@name='NoOfFourierLines']/value").text)
    data['Nz'] = get_yaps_by_name(root,'iNoOfFourierPartitions',lambda x:int(x))
    data['NxRecon'] = get_yaps_by_name(root,'iRoFTLength',lambda x:int(x))
    data['NyRecon'] = get_yaps_by_name(root,'iPEFTLength',lambda x:int(x))
    
    if data['Nz'] is 1:
        data['NzRecon'] = 1
    else:
        data['NzRecon'] = get_yaps_by_name(root,'i3DFTLength',lambda x:int(x))

    data['NslicePerConcat'] = get_yaps_by_name(root,'ushSlicePerConcat',lambda x:int(x))

    ### Partial Fourier Mode and Parameters
    data['PCAlgorithm'] = get_yaps_by_name(root,'lPCAlgorithm',lambda x:int(x))
    data['NoOfPhaseCorrColumns'] = get_yaps_by_name(root,'lNoOfPhaseCorrColumns',lambda x:int(x),data['Nx']/2)
    data['NoOfPhaseCorrLines'] = get_yaps_by_name(root,'lNoOfPhaseCorrLines',lambda x:int(x),data['NyAll']/2)
    data['NoOfPhaseCorrPartitions'] = get_yaps_by_name(root,'lNoOfPhaseCorrPartitions',lambda x:int(x),data['NzAll']/2)
    data['ColSlopeLength'] = get_yaps_by_name(root,'lColSlopeLength',lambda x:int(x),data['Nx']/4)
    # I think there's a mistake here in the MATLAB code: ColSlopeLength defined again instead of LinSlopeLength.
    # I will write it how I think it should be and we'll go from there.
    data['LinSlopeLength'] = get_yaps_by_name(root,'lLinSlopeLength',lambda x:int(x),data['NyAll']/4)
    data['ParSlopeLength'] = get_yaps_by_name(root,'lParSlopeLength',lambda x:int(x),data['NzAll']/4)
    
    ### Raw data correction factors
    # We're now back to the MeasYaps portion of the xml document
    root = ET.fromstring(my_xmlstr)
    data['CorrFactor'] = np.ones(data['Nc'])
    for c in range(data['Nc']):
        text = 'axRawDataCorrectionFactor[0][%d].dRe' % c
        if my_xmlstr.find(text) < 0:
            data['CorrFactor'][c] = 1
        else:
            data['CorrFactor[c]'] = float(get_val_by_text(root,text).text)

        text = 'axRawDataCorrectionFactor[0][%d].dIm' % c
        if my_xmlstr.find(text) >= 0:
            data['CorrFactor'][c] = data['CorrFactor'][c] + i*float(get_val_by_text(root,text).text)


    ### FFT Correction Factors
    data['FFTCorrFactor'] = np.ones(data['Nc'])
    if resetFFTscale is False:
        data['FFTCorrFactor'] = np.ones(data['Nc'])
        for c in range(data['Nc']):
            text = 'asCoilSelectMeas[0].aFFT_SCALE[%d].flFactor' % c
            data['FFTCorrFactor'][c] = float(get_val_by_text(root,text).text)


    ### For PC Angio
    data['Nset'] = 1
    text = 'sAngio.ucPCFlowMode'
    if my_xmlstr.find(text) > 0:
        data['PCMRAFlag'] = int(get_val_by_text(root,text).text,16)
    else:
        data['PCMRAFlag'] = 0

    if data['PCMRAFlag'] is 1:
        text = 'sAngio.sFlowArray.lSize'
        if my_xmlstr.find(text) < 0:
            data['Nset'] = int(get_val_by_text(root,text).text)


    ### Recalculation of partial Fourier factors and EPI/turbo factor for EPI and TSE
    data['fractionPE'] = float(data['Ny'])/float(data['NyAll'])
    data['fraction3D'] = float(data['Nz'])/float(data['NzAll'])
    data['EPIFactor'] = np.around(data['fractionPE']*data['EPIFactor'])
    data['nEPITrain'] = data['Ny']/data['EPIFactor']
    data['turboFactor'] = np.around(data['fractionPE']*data['turboFactor'])
    data['nTSETrain'] = data['Ny']/data['turboFactor']

    data['Nc0'] = data['Nc']
    if readOneCoil == 1:
        data['Nc'] = 1
    else:
        data['Nc'] = data['Nc0']
        
    ### Calculation of the number of valid k-space readouts and k-space data matrix dimensions
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

    ### Data Readout and Reordering
    # Read k-space data
    noiseMeasCounter = 0
    noiseMeas = np.zeros((data['NxOS'],data['Nc']))
    navigatorPrep = 0
    LineN = -1
    Ndr = 1

    #for r in range(data['Ndr']):
    #    xCoil = r
        
    
    # Give back the dictionary of values
    return(data)
    

readMeasDataVB15('test-data/test.dat')
