#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
"""Module doctsring

Routine Name:  adaptive_median.py

Desc:   This routine is run from the command line with one or more arguments
	and one or more input image filenames.  Optional arguments include
	Help, Verbose, and the filter parameters Window and Threshold.

        Window is specified as the window size (ws) where the width of the 
        square window (W) equals 2*ws + 1 and the range is 1..5.

        Threshold is defined as t*S (where S is the adaptive filter parameter)
        such that t = 0 is the most aggresive (a standard median filter) and
        higher values of 't' will reduce the probability of pixel replacement.
        This effectively filters out the more outlying pixels.

	Requires Python 2.7, pillow (PIL) of recent vintage, and numpy.

Arguments:

Name            I/O     Description
----            ---     -----------
-h|--help       N/A     Prints module docstring
-v|--verbose    N/A     Prints extra more verbose messages
-w|--window     N/A     Sets the filter window size (must be a scalar
                        between 1 and 5).  Window size (ws) is defined as
			W = 2*ws + 1 so that W = 3 is a 3x3 filter window.
-t|--threshold  N/A     Sets the adaptive threshold (0=normal median
                        behavior).  Higher values reduce the "aggresiveness"
			of the filter.

filename(s)     In      One or more gray-scale image files

usage:

adaptive_median.py [-hvwt|--help --verbose --window=[1..5] --threshold=[N]] <filename> [<filename>...]

Revision History:
Date        Name         Description
----        ----         -----------
08-28-2005  S.L. Arnold  Initial implementation with internal (numarray) sort.
09-18-2005  S.L. Arnold  Added timing routine and prepped for calling SWIG-
                         wrapped functions.
"""

##--------------------------------------
import sys, time
#import medians_1D
from numpy import *
#import Image
from PIL import Image
from PIL.Image import core as _imaging

def process(image, size, window, threshold, spam):

    ## set filter window and image dimensions
    W = 2*window + 1
    xlength, ylength = size
    vlength = W*W
    if spam:
        print 'Image length in X direction: ', xlength
        print 'Image length in Y direction: ', ylength
        print 'Filter window size: ', W, 'x', W

    ## create 2-D image array and initialize window
    image_array = reshape(array(image, dtype=int16), (ylength,xlength))
    filter_window = array(zeros((W,W)))
    target_vector = array(zeros(vlength))
    pixel_count = 0

    try:
        ## loop over image with specified window W
        for y in range(window, ylength-(window+1)):
            for x in range(window, xlength-(window+1)):
            ## populate window, sort, find median
                filter_window = image_array[y-window:y+window+1,x-window:x+window+1]
                target_vector = reshape(filter_window, ((vlength),))
                ## internal sort
                median = demo(target_vector, vlength)
                ##median = medians_1D.quick_select(target_vector, vlength)
	        ## check for threshold
                if not threshold > 0:
                    image_array[y,x] = median
                    pixel_count += 1
                else:
                    scale = zeros(vlength)
                    for n in range(vlength):
                        scale[n] = abs(target_vector[n] - median)
                    scale = sort(scale)
                    Sk = 1.4826 * (scale[vlength/2])
                    if abs(image_array[y,x] - median) > (threshold * Sk):
                        image_array[y,x] = median
                        pixel_count += 1

    except TypeError:
        print "Error in processing function:", err
        sys.exit(2)
        ## ,NameError,ArithmeticError,LookupError

    print pixel_count, "pixel(s) filtered out of", xlength*ylength
    ## convert array back to sequence and return
    return reshape(image_array, (xlength*ylength,)).tolist()

def demo(target_array, array_length):
    sorted_array = sort(target_array)
    median = sorted_array[array_length/2]
    return median

class Timer(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.secs = self.end - self.start
        self.msecs = self.secs * 1000  # millisecs
        if self.verbose:
            print 'elapsed time: %f ms' % self.msecs

def main(argv):

    import os, getopt, sys

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
        print "Usage: %s [-h|v|--window=[1..5]|--threshold=[0..N]] <filename>" % (argv[0],)
        print "Demonstrates adaptive median filtering on gray-scale images."
        sys.exit(2)

    # Obligatory spam variable; controls verbosity of the output
    spam = False
    
    # window = ws, where the filter window W = 2*ws + 1, 
    # ie, ws = 1 is a 3x3 window (W=3)
    window = 1
    threshold = 0.

    for o, a in args:
        if o in ("-h", "--help"):
            print __doc__
            sys.exit(0)
        if o in ("-v", "--verbose"):
            spam = True
            verbose = True

    if spam:
        print "options =", args
        print "filenames =", filenames

    try:
        for o in args[:]:
            if o[0] == '--threshold' and o[1] != '':
                threshold = float(o[1])
                args.remove(o)
                break
            elif o[0] == '--threshold' and o[1] == '':
                print "The --threshold option requires an argument."
                sys.exit(2)
        for o in args[:]:
            if o[0] == '--window' and o[1] != '':
                window = int(o[1])
                args.remove(o)
                break
            elif o[0] == '--window' and o[1] == '':
                print "The --window option requires an argument."
                sys.exit(2)
    except ValueError:
        print "Incompatible parameter", o[1],".", " Option must be a number."
        sys.stderr.write
        sys.exit(2)
    except TypeError, err:
        print "Parameter error:", err
        sys.exit(2)

    if threshold < 0.:
        print "The threshold must be a non-negative real value (default=0)."
	sys.exit(2)

    if not (1 <= window <= 5):
        print "The window size must be an integer between 1 and 5 (default=1)."
	sys.exit(2)
    
    if not filenames:
        print "Please specify one or more gray-scale input files."

    if spam:
        print "window =", window
        print "threshold =", threshold

    image_count = 0
    filter_time = 0.

    for filename in filenames:
        try:
            infile = open(filename, "rb")
        except IOError, err:
            print "Input file error:", err
            if spam:
                print "Please check the name(s) of your input file(s)."
            os.close(sys.stderr.fileno())
            sys.exit(2)

	try:
	    pil_image = Image.open(infile)
	    if pil_image.mode == 'P':
	        if spam:
	            print "Original image mode: ",pil_image.mode
	        pil_image = pil_image.convert("L")
	except IOError:
	    print "Cannot parse input image format.", pil_image
	if spam:
	    print "Input image format: ", pil_image.format
	    print "Input image size: ", pil_image.size
	    print "Working image mode: ",pil_image.mode

	## Convert the PIL image object to a python sequence (list)
	input_sequence = list(pil_image.getdata())

	try:
            ## filter input image sequence
            with Timer() as t:
                output_sequence = process(input_sequence, pil_image.size, window, threshold, spam)

            ## init output image
            file, ext = os.path.splitext(filename)
            outfile = "new_" + file + ext
            try:
                output_image = Image.new(pil_image.mode, pil_image.size, None)
                output_image.putdata(output_sequence)
                output_image.save(outfile, pil_image.format)
                if spam:
                    print "Output image name: ", outfile

            except IOError, err:
                print "Output file error:", err
                if spam:
                    print "Cannot create output image for ", input_image, "."
                    print "  Continuing with next available file..."
                continue

        except MemoryError, err:
            sys.stderr.write(err)
            if spam:
                print "Not enough memory to create output image for ", input_image, "."
                print "  Continuing with next available file..."
            continue

        infile.close()
        image_count += 1

    print image_count, " images filtered in %s sec." % t.secs

if __name__ == "__main__":
    main(sys.argv)

