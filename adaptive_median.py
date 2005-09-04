#!/usr/bin/env python
"""Module doctsring

Routine Name:  adaptive_median.py

Desc:   This routine is run from the command line with one or more arguments
	and an input image filename; it may support more than one image file
	in the future, but currently only supports one image filename as the
	last (and only required) argument.  The optional arguments include
	Help, Verbose, and the filter parameters Window and Threshold.

        Window is specified as the window size (ws) where the width of the 
        square window (W) equals 2*ws + 1 and the range is 1..5.

        Threshold is defined as t*S (where S is the adaptive filter parameter)
        such that t = 0 is the most aggresive (a standard median filter) and
        higher values of 't' will reduce the probability of pixel replacement.
        This effectively filters out the more outlying pixels.

	Requires Python Imaging Library (PIL) of recent vintage.
       
Arguments:

Name            I/O     Description
----            ---     -----------
filename(s)     In      One or more gray-scale image files

-h|--help       N/A     Prints module docstring
-v|--verbose    N/A     Prints extra more verbose messages
-w|--window     N/A     Sets the filter window size (must be a scalar
                        between 1 and 5).  Window size (ws) is defined as
			W = 2*ws + 1 so that W = 3 is a 3x3 filter window.
-t|--threshold  N/A     Sets the adaptive threshold (0=normal median
                        behavior).  Higher values reduce the "aggresiveness"
			of the filter.

usage:

adaptive_median.py [-hv|--help --verbose --window=[1..5] --threshold=[N]] <filename> [<filename>...]

Revision History:
Date        Name         Description
----        ----         -----------
08-28-2005  S.L. Arnold  Initial implementation with internal sort.
"""

##--------------------------------------
import sys
## from time import time, gmtime, strftime, strptime, mktime, sleep

def filter(image, size, window, threshold, verbose):

    ## set image dimensions
    W = 2*window + 1
    xlength, ylength = size
    if verbose:
        print "Image length in X direction: ", xlength
	print "Image length in Y direction: ", ylength

    ## loop over y and x
    
    ## check for threshold

    return image

def main(argv):

    import os, getopt, sys, Image

    global filename

    ## Do the right thing with boolean values for all known Python versions.
    try:
        True, False
    except NameError:
        (True, False) = (1, 0)

    try:
        args, filenames = getopt.getopt(argv[1:], "hv", ["help", "verbose", "window=", "threshold="])
    except getopt.error, msg:
        args = "dummy"
        print msg
        print "Usage: %s [-h|v|--window=[1..5]|--threshold=[0..N]] <filename>" % (argv[0],)
        print "Demonstrates adaptive median filtering on gray-scale images."
        sys.exit(2)

    verbose = False
    # window = ws, where the filter window W = 2*ws + 1, 
    # ie, ws = 1 is a 3x3 window (W=3)
    window = 1
    threshold = 0.0

    for o, a in args:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-v", "--verbose"):
            verbose = True
    if verbose:
        print "options =", args
        print "filenames =", filenames

    for o in args[:]:
        if o[0] == '--window' and o[1] != '':
            window = int(o[1])
            args.remove(o)
            break
        elif o[0] == '--window' and o[1] == '':
            print "The --window option requires an argument."
            sys.exit(2)
        if o[0] == '--threshold' and o[1] != '':
            threshold = float(o[1])
            args.remove(o)
            break
        elif o[0] == '--threshold' and o[1] == '':
            print "The --threshold option requires an argument."
            sys.exit(2)

    if not (1 <= window <= 5):
        print "The window size must be an integer between 1 and 5."
	sys.exit(2)
    
    if not filenames:
        print "Please specify one or more gray-scale input files."

    image_count = 0

    for filename in filenames:
        try:
            infile = open(filename, "rb")
        except IOError, err:
            sys.stderr.write(err)
            if verbose:
                print "Please check the name(s) of your input file(s)."
            os.close(sys.stderr.fileno())
            sys.exit(2)

	try:
	    pil_image = Image.open(infile)
	    if pil_image.mode == 'P':
	        if verbose:
	            print "Original image mode: ",pil_image.mode
	        pil_image = pil_image.convert("L")
	except IOError:
	    print "Cannot parse input image format.", pil_image
	if verbose:
	    print "Input image format: ", pil_image.format
	    print "Input image size: ", pil_image.size
	    print "Working image mode: ",pil_image.mode
	    ## print "Displaying input image...", pil_image
	    ## pil_image.show()
	size = pil_image.size
	## Convert the PIL image object
	input_sequence = list(pil_image.getdata())
	try:
	    ## filter input image sequence
	    output_sequence = filter(input_sequence, size, window, threshold, verbose)
	    ## init output image
	    file, ext = os.path.splitext(filename)
	    outfile = "new_" + file + ext
	    try:
	        output_image = Image.new(pil_image.mode, pil_image.size, None)
	        output_image.putdata(output_sequence)
	        output_image.save(outfile, pil_image.format)
	        if verbose:
	            print "Output image name: ", outfile

	    except IOError, err:
	        sys.stderr.write()
		if verbose:
		    print "Cannot create output image for ", input_image, "."
		    print "  Continuing with next available file..."
		continue
	    
	    ## output_image.show()

        except MemoryError, err:
	    sys.stderr.write()
	    if verbose:
                print "Not enough memory to create output image for ", input_image, "."
		print "  Continuing with next available file..."
            continue

        infile.close()
	image_count = image_count + 1

    print image_count, " image(s) filtered."

if __name__ == "__main__":
    main(sys.argv)

