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

        Requires Python, pillow (PIL) of recent vintage, and numpy.

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

adaptive_median.py [-hvwt|--help --verbose --window=[1..5] --threshold=[N]] <filename> [...]

Revision History:
Date        Name         Description
----        ----         -----------
08-28-2005  S.L. Arnold  Initial implementation with internal (numarray) sort.
09-18-2005  S.L. Arnold  Added timing routine and prepped for calling SWIG-
                         wrapped functions.
11-28-2013  S.L. Arnold  Updated to work with Python 2.7, pillow, and numpy.
10-14-2020  S.L. Arnold  Merge Jupyter PR and port to python3.
"""

##--------------------------------------
import getopt
import os
import sys
import time

# import medians_1D
import numpy as np
from PIL import Image


def process(image, size, window=1, threshold=0., spam=False):

    ## set filter window and image dimensions
    filter_window = 2*window + 1
    xlength, ylength = size
    vlength = filter_window*filter_window
    if spam:
        print('Image length in X direction: {}'.format(xlength))
        print('Image length in Y direction: {}'.format(ylength))
        print('Filter window size: {0} x {0}'.format(filter_window))

    ## create 2-D image array and initialize window
    image_array = np.reshape(np.array(image, dtype=np.uint8), (ylength, xlength))
    filter_window = np.array(np.zeros((filter_window, filter_window)))
    target_vector = np.array(np.zeros(vlength))
    pixel_count = 0

    try:
        ## loop over image with specified window filter_window
        for y in range(window, ylength-(window+1)):
            for x in range(window, xlength-(window+1)):
            ## populate window, sort, find median
                filter_window = image_array[y-window:y+window+1, x-window:x+window+1]
                target_vector = np.reshape(filter_window, ((vlength),))
                ## numpy sort
                median = median_demo(target_vector, vlength)
                ## C median library
                # median = medians_1D.quick_select(target_vector, vlength)
            ## check for threshold
                if not threshold > 0:
                    image_array[y, x] = median
                    pixel_count += 1
                else:
                    scale = np.zeros(vlength)
                    for n in range(vlength):
                        scale[n] = abs(int(target_vector[n]) - int(median))
                    scale = np.sort(scale)
                    Sk = 1.4826 * (scale[vlength//2])
                    if abs(int(image_array[y, x]) - int(median)) > (threshold * Sk):
                        image_array[y, x] = median
                        pixel_count += 1

    except TypeError as err:
        print('Error in processing function:'.format(err))
        sys.exit(2)
        ## ,NameError,ArithmeticError,LookupError

    print('{} pixel(s) filtered out of {}'.format(pixel_count, xlength*ylength))
    ## convert array back to sequence and return
    return np.reshape(image_array, (xlength*ylength)).tolist()


def median_demo(target_array, array_length):
    sorted_array = np.sort(target_array)
    median = sorted_array[array_length//2]
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
            print('elapsed time: {} ms'.format(self.msecs))


def main(argv):

    filenames = None

    try:
        args, filenames = getopt.getopt(argv[1:],
                                        'hvwt',
                                        ['help', 'verbose', 'window=', 'threshold='])
    except getopt.error as msg:
        args = "dummy"
        print(msg)
        print('Usage: {} [-h|v|--window=[1..5]|--threshold=[0..N]] <filename>'.format(argv[0]))
        print('Demonstrates adaptive median filtering on gray-scale images.')
        sys.exit(2)

    # Obligatory spam variable; controls verbosity of the output
    spam = False

    # window = ws, where the filter_window = 2*ws + 1,
    # ie, ws = 1 is a 3x3 window (filter_window=3)
    window = 1
    threshold = 0.

    for o, a in args:
        if o in ("-h", "--help"):
            print(__doc__)
            sys.exit(0)
        if o in ("-v", "--verbose"):
            spam = True

    if spam:
        print('options = {}'.format(args))
        print('filenames = {}'.format(filenames))

    try:
        for o in args[:]:
            if o[0] == '--threshold' and o[1] != '':
                threshold = float(o[1])
                args.remove(o)
            if o[0] == '--threshold' and o[1] == '':
                print('The --threshold option requires an argument.')
                sys.exit(2)
        for o in args[:]:
            if o[0] == '--window' and o[1] != '':
                window = int(o[1])
                args.remove(o)
            if o[0] == '--window' and o[1] == '':
                print('The --window option requires an argument.')
                sys.exit(2)
    except ValueError as err:
        print('Parameter error: {}\nOption must be a number.'.format(err))
        sys.exit(2)
    except TypeError as err:
        print('Parameter error: {}'.format(err))
        sys.exit(2)

    if threshold < 0.:
        print('The threshold must be a non-negative real value (default=0).')
        sys.exit(2)

    if not 1 <= window <= 5:
        print('The window size must be an integer between 1 and 5 (default=1).')
        sys.exit(2)

    if not filenames:
        print('Please enter one or more image filenames.')
        sys.exit(2)

    if spam:
        print('window = {}'.format(window))
        print('threshold = {}'.format(threshold))

    image_count = 0
    filter_time = 0.

    for filename in filenames:
        try:
            infile = open(filename, "rb")
        except IOError as err:
            print('Input file error: {}'.format(err))
            if spam:
                print('Please check the name(s) of your input file(s).')
            os.close(sys.stderr.fileno())
            sys.exit(2)

        try:
            pil_image = Image.open(infile)
            if pil_image.mode == 'P':
                if spam:
                    print('Original image mode: {}'.format(pil_image.mode))
                pil_image = pil_image.convert('L')
        except IOError:
            print('Cannot parse input image format: {}'.format(pil_image))
        if spam:
            print('Input image format: {}'.format(pil_image.format))
            print('Input image size: {}'.format(pil_image.size))
            print('Working image mode: {}'.format(pil_image.mode))

        ## Convert the PIL image object to a python sequence (list)
        input_sequence = list(pil_image.getdata())

        try:
            ## filter input image sequence
            with Timer(spam) as ttimer:
                output_sequence = process(input_sequence, pil_image.size, window, threshold, spam)

            ## init output image
            file, ext = os.path.splitext(filename)
            outfile = "new_" + file + ext
            try:
                output_image = Image.new(pil_image.mode, pil_image.size, None)
                output_image.putdata(output_sequence)
                output_image.save(outfile, pil_image.format)
                if spam:
                    print('Output image name: {}'.format(outfile))

            except IOError as err:
                print('Output file error: {}'.format(err))
                if spam:
                    print('Cannot create output image for {}.'.format(input_image))
                    print('  Continuing with next available file...')
                pass

        except MemoryError as err:
            sys.stderr.write(err)
            if spam:
                print('Not enough memory to create output image for {}.'.format(input_image))
                print('  Continuing with next available file...')
            pass

        infile.close()
        image_count += 1

    print('{} images filtered in {:10.4f} sec.'.format(image_count, ttimer.secs))


if __name__ == "__main__":
    main(sys.argv)
