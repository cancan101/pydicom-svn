# time_test.py
"""Try reading large sets of files, profiling how much time it takes"""
# Copyright (c) 2008 Darcy Mason
# This file is part of pydicom, relased under an MIT license.
#    See the file license.txt included with this distribution, also
#    available at http://pydicom.googlecode.com

import os.path

# EDIT THIS SECTION --------------------------
#    to point to local temp directory, and to a set of >400 DICOM files of same size to work on
# I used images freely available from http://pcir.org
tempfile = "/tmp/pydicom_stats"
# I testImages freely available from pcir.org
location_base = r"/Users/darcy/testdicom/"
# location_base = r"/Volumes/Disk 1/testdicom/"  # Network disk location
locations = ["77654033_19950903/77654033/19950903/CT2/",
             "98890234_20010101/98890234/20010101/CT5/",
             "98890234_20010101/98890234/20010101/CT6/",
             "98890234_20010101/98890234/20010101/CT7/",

            ]
locations = [os.path.join(location_base, location) for location in locations]
# -------------------------------------------------------
import glob
import dicom
from dicom.filereader import read_partial, _at_pixel_data
from dicom.filebase import DicomFileLike    
from dicom.filebase import DicomStringIO

from time import time
import cProfile # python >=2.5
import pstats
import random

rp = read_partial
filenames = []
for location in locations:
    loc_list = glob.glob(os.path.join(location, "*"))
    filenames.extend((x for x in loc_list if not x.startswith(".")))

assert len(filenames) >= 400, "Need at least 400 files" # unless change slices below
random.shuffle(filenames) # to make sure no bias for any particular file
print "Sampling from %d files" % len(filenames), ". Each test gets 100 distinct files"

# Give each test it's own set of files, to avoid reading something in cache from previous test
filenames1 = filenames[:100] # keep the time to a reasonable amount (~2-25 sec)
filenames2 = filenames[100:200]
filenames3 = filenames[200:300]
filenames4 = filenames[300:400]

def test_full_read():
    rf = dicom.read_file
    ds = [rf(fn) for fn in filenames1]

def test_partial():
    rp = read_partial
    ds = [rp(DicomFileLike(open(fn, 'rb')), stop_when=_at_pixel_data) for fn in filenames2]

def test_mem_read_full():
    rf = dicom.read_file
    str_io = DicomStringIO
    memory_files = (str_io(open(fn, 'rb').read()) for fn in filenames3)
    ds = [rf(memory_file) for memory_file in memory_files]

def test_mem_read_small():
    rf = dicom.read_file
    str_io = DicomStringIO # avoid global lookup, make local instead
    memory_files = (str_io(open(fn, 'rb').read(4000)) for fn in filenames4)
    ds = [rf(memory_file) for memory_file in memory_files]

def test_python_read_files():
    all_files = [open(fn, 'rb').read() for fn in filenames4]

if __name__ == "__main__":
    for testrun in ['test_full_read()','test_partial()', 
                    'test_mem_read_full()',
                    # 'test_mem_read_small()',
                    'test_python_read_files()',
                     ]:
        cProfile.run(testrun, tempfile)
        p = pstats.Stats(tempfile)
        print "---------------"
        print testrun
        print "---------------"
        p.strip_dirs().sort_stats('time').print_stats(5)

