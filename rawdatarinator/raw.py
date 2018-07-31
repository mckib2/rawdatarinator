from rawdatarinator.readMeasDataVB15 import readMeasDataVB15

def raw(*args,**kwargs):
    '''Alias for readMeasDataVB15.

    Use same interface as readMeasDataVB15.
    '''
    return(readMeasDataVB15(*args,**kwargs))

if __name__ == '__main__':
    from rawdatarinator.readMeasDataVB15 import main
    import sys
    main(sys.argv[1:])
