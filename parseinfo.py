# IDEA:
# Parse the quasi-XML structure into a dictionary

import regex

# load in the data
with open('test-data/info.txt','r') as f:
    info = f.read()

# For all the ParamStrings
ParamString = regex.findall('<ParamString\."(.*)">\s*{\s*"(.*)"\s*}\s*',info)

# For all the ParamLongs
ParamLong = regex.findall('<ParamLong\."(.*)">\s*{\s*(\d*)\s*}\s*',info)

ParamLongArrays = regex.findall('<ParamLong\."(.*)">\s*{\s(.*)\s}\s*',info)

# For all the ParamBools
ParamBool = regex.findall('<ParamBool\."(.*)">\s*{\s*"(.*)"\s*}\s*',info)

# Turn all the lists into dictionaries and deal with duplicate keys
ParamStringDict = {}
for idx,val in enumerate(ParamString):
    key = str(idx) + val[0] if val[0] in ParamStringDict else val[0]  
    ParamStringDict.update({key : val[1::]})

ParamLongDict = {}
for idx,val in enumerate(ParamLong):
    key = str(idx) + val[0] if val[0] in ParamLongDict else val[0]
    value = 0.0 if val[1] == '' else float(val[1])
    ParamLongDict.update({key : value})

# Go back and get everything to make sure we get lists of numbers
ParamLongArrayDict = {}
for idx,val in enumerate(ParamLongArrays):
    key = str(idx) + val[0] if val[0] in ParamLongArrayDict else val[0]
    ParamLongArrayDict.update({key : val[1::]})

# Get only the arrays of numbers by removing duplicate keys
a = ParamLongArrayDict.copy()
for key in a:
    if key in ParamLongDict:
        ParamLongArrayDict.pop(key)

ParamBoolDict = {}
for idx,val in enumerate(ParamBool):
    key = str(idx) + val[0] if val[0] in ParamBoolDict else val[0]
    value = True if val[1] == 'true' else False
    ParamBoolDict.update({key : value})

# make one big dictionary
Params = dict(ParamLongDict)
Params.update(ParamLongArrayDict)
Params.update(ParamBoolDict)

print(Params['ucDimension'])
