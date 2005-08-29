#!/usr/bin/env python
"""Module doctsring

Routine Name:  adaptive_median.py

Desc:  This routine is run from the command line with one or more arguments and an
       input image filename; it may support more than one image file in the future,
       but currently only supports one image filename as the last (and only required)
       argument.  The optional arguments include Help, Verbose, and the filter
       parameters Window and Threshold.

       Window is specified as the window size (ws) where the width of the square
       window (W) equals 2*ws + 1 and the range is 1..5.

       Threshold is defined as t*S (where S is the adaptive filter parameter) such
       that t = 0 is the most aggresive (a standard median filter) and higher values 
       of 't' will reduce the probability of pixel replacement.  This effectively
       filters out the more outlying pixels.
       
Arguments:

Name            I/O     Description
----            ---     -----------
filename(s)     In      One or more gray-scale image files

-h|--help       N/A     Prints module docstring
-v|--verbose    N/A     Prints extra more verbose messages
-w|--window     N/A     Sets the filter window size (must be a scalar
                        between 1 and 5).  Window size (ws) is defined as
			W = 2*ws + 1 so that ws = 1 is a 3x3 window.
-t|--threshold  N/A     Sets the adaptive threshold (0=normal median
                        behavior).  Higher values reduce the "aggresiveness"
			of the filter.

usage:

adaptive_median.py [-hvwt|--help --verbose --window=[1..5] --threshold=[N]] <filename> [<filename>...]

Revision History:
Date        Name         Description
----        ----         -----------
08-28-2005  S.L. Arnold  Initial implementation with internal sort.
"""

##--------------------------------------
import sys
## from time import time, gmtime, strftime, strptime, mktime, sleep

def filter(input_image, window, threshold, verbose):

    ## size image

    ## init output image

    ## loop over y and x

    ## check for threshold

    output_image = input_image

    return output_image

def main(argv):

    import os, getopt, sys, Image

    global filename

    ## Do the right thing with boolean values for all known Python versions.
    try:
        True, False
    except NameError:
        (True, False) = (1, 0)

    try:
        args, filenames = getopt.getopt(argv[1:], "hvwt", ["help", "verbose", "window=", "threshold="])
    except getopt.error, msg:
        args = "dummy"
        print msg
        print "Usage: %s [-h|v|w|--window=[1..5]|t|--threshold=[0..N]] <filename>" % (argv[0],)
        print "Demonstrates adaptive median filtering on gray-scale images."
        sys.exit(2)

    verbose = False
    window = 0  # window size => W = 2*ws + 1, ie, ws = 1 is a 3x3 window (W=3)
    threshold = 0.0

    for o, a in args:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-v", "--verbose"):
            verbose = True
    for o in args[:]:
        if o[0] == '--window' and o[1] != '':
            window = o[1]
            args.remove(o)
            break
        elif o[0] == '--window' and o[1] == '':
            print "The --window option requires an argument."
            sys.exit(2)
        if o[0] == '--threshold' and o[1] != '':
            threshold = o[1]
            args.remove(o)
            break
        elif o[0] == '--threshold' and o[1] == '':
            print "The --threshold option requires an argument."
            sys.exit(2)

    if verbose:
        print "options =", args
        print "filenames =", filenames

    if not filenames:
        print "Please specify one or more gray-scale input files"

    for filename in filenames:
        try:
            infile = open(filename, "rb")
        except IOError, err:
            sys.stderr.write(err)
            if verbose:
                print "Please check the name(s) of your input file(s)"
            os.close(sys.stderr.fileno())
            sys.exit(2)

	try:
	    input_image = Image.open(infile)
	except IOError:
	    print "cannot parse input image format", input_image
	if verbose:
	    print "Input image format: ", input_image.format
	    print "Input image size: ", input_image.size
	    print "Input image mode: ",input_image.mode
	    ## print "Displaying input image...", input_image
	    ## input_image.show()
	## Do stuff with the image file
	try:
	    output_image = filter(input_image, window, threshold, verbose)
	    outfile = "new_" + os.path.splitext(filename)[0] + os.path.splitext(filename)[1]
	    output_image.save(outfile, input_image.format)

        except IOError, err:
	    sys.stderr.write()
	    if verbose:
                print "cannot create output image for", input_image
		print "  Continuing with next available file..."
            continue

        infile.close()
	## outfile.close()

if __name__ == "__main__":
    main(sys.argv)

