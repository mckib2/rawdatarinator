from infoparser import raw2xml
import xml.etree.ElementTree as ET
import re

def get_val(root,search):
    found_flag = False
    for el in root.iter():
        if found_flag:
            return(el)
        if el.text == search:
            # We want the next el
            found_flag = True
    
def readMeasDataVB15(filename):
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
            val = get_val(root,tup[1]).text
            
        # Evaluate anonymous function if provided
        afun = tup[3]
        if afun is not None:
            val = afun(val)

        # Store the value in the dictionary
        print('Result: %s %s' % (type(val),val))
        data[tup[0]] = val

    # Give back the dictionary of values
    return(data)
    

readMeasDataVB15('test-data/test.dat')
