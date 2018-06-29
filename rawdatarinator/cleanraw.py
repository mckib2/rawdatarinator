import re
import numpy as np

def cleanraw(filename):
    # Give some test data
    with open(filename,'rb') as f:
        num = np.fromfile(f,dtype=np.int32,count=1)[0]
        info = f.read(num-4)

    # Unfortunately Windows exists
    info = info.replace(b'\r',b' ').replace(b'\0',b' ')

    # we want to ignore some junk before the <XProtocol>
    start = info.find(b'<XProtocol>') - 1
    info = info[start:]

    # We get the same kind of junk before <XProtocol> and after Dicom
    trouble = re.search(r'Dicom.*<XProtocol>'.encode(),info)
    if trouble is not None:
        info = info.replace(info[trouble.start():trouble.end()],b'<Dicom> <XProtocol>')

    # And again with Meas...<XProtocol>
    trouble = re.search(r'.Meas.*<XProtocol>'.encode(),info)
    if trouble is not None:
        info = info.replace(info[trouble.start():trouble.end()],b'<Meas> <XProtocol>')

    # Guess what - with MeasYaps...### ASC..., too
    trouble = re.search(r'.MeasYaps.*###'.encode(),info)
    if trouble is not None:
        info = info.replace(info[trouble.start():trouble.end() - len('###')],b'\n <MeasYaps>')

    # Found another...
    trouble = re.search(r'.Phoenix.*<XProtocol>'.encode(),info)
    if trouble is not None:
        info = info.replace(info[trouble.start():trouble.end()],b'<Phoenix> <XProtocol>')

    # This time we're missing a breakline
    trouble = re.search(r'.Spice.*<XProtocol>'.encode(),info)
    if trouble is not None:
        info = info.replace(info[trouble.start():trouble.end()],b'\n<Spice> <XProtocol>\n')

    # Get rid of everything at the end we don't want right now
    end = info.rfind(b'}') + 1
    info = info[1:end]

    return(info.decode('ascii'))
