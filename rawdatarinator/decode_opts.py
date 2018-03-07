import sys

def decode_simple_opts(options,args,fun):
    
    if len(args) < 1:
        print('Requires filename argument!')
        print("Use option '-h' for help")
        sys.exit(2)
        return(-1)
    elif '-h' in args:
        print(fun.__doc__)
        return(0)
    
    # The first argument should be the filename
    if args in list(options.keys()):
        print('The first argument should be the filename!')
        sys.exit(2)
        return(-1)
        
    for opt in args[1:]:
        if opt not in options.keys():
            print("Skipping invalid option '%s', use '-h' for help" % opt)
        else:
            options[opt][1] = not options[opt][1]

    # Run the function with decoded options
    pargs = dict()
    for opt,tup in options.items():
        pargs[tup[0]] = tup[1]

    fun(args[0],**pargs)
