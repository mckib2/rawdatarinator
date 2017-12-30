import re
import numpy as np

def cleanraw(filename):
    # Give some test data
    with open(filename,'r') as f:
        num = np.fromfile(f,dtype=np.int32,count=1)
        info = f.read(num-4)
        
    # we want to ignore some junk before the <XProtocol>
    start = info.find('<XProtocol>') - 1
    info = info[start:]
        
    # We get the same kind of junk before <XProtocol> and after Dicom
    trouble = re.search(r'Dicom.*<XProtocol>',info)
    info = info.replace(info[trouble.start():trouble.end()],'<Dicom> <XProtocol>')
        
    # And again with Meas...<XProtocol>
    trouble = re.search(r'.Meas.*<XProtocol>',info)
    info = info.replace(info[trouble.start():trouble.end()],'<Meas> <XProtocol>')
        
    # Guess what - with MeasYaps...### ASC..., too
    trouble = re.search(r'.MeasYaps.*###',info)
    info = info.replace(info[trouble.start():trouble.end() - len('###')],'\n <MeasYaps>')
        
    # Found another...
    trouble = re.search(r'.Phoenix.*<XProtocol>',info)
    info = info.replace(info[trouble.start():trouble.end()],'<Phoenix> <XProtocol>')
        
    # This time we're missing a breakline
    trouble = re.search(r'.Spice.*<XProtocol>',info)
    info = info.replace(info[trouble.start():trouble.end()],'\n<Spice> <XProtocol>\n')
        
    # Get rid of everything at the end we don't want right now
    end = info.rfind('}') + 1
    info = info[1:end]

    return(info)
