adaptive-median
===============

Adaptive-median image filter

This is just a python implementation of an adaptive median image filter, 
which is essentially a despeckling filter for grayscale images.  The 
other piece (which you can disable by commenting out the import line 
for medians_1D) is a set of example C median filters and swig wrappers 
(see the medians-1D repo for that part).  This part is not fully working 
yet in terms of passing python arrays to C (contributions welcome).

Steve Arnold <stephen.arnold42 _at_ gmail.com>

