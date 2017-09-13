# pylint: disable=line-too-long,C0103,C0330
from __future__ import print_function
'''
To use this:

import sys
sys.path.append("/HFIR/CG2/shared/scripts")

from file_helper import CG2
'''
import os
import errno
import unittest
import shutil
import re
from collections import defaultdict, OrderedDict

try:
    from mantid.simpleapi import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class Experiment(object):
    _instruments = {
        "CG2": "CG2",
        "CG3": "BioSANS",
    }

    def __init__(self, beamline, ipts_number, exp_number):
        self._beamline = beamline
        self._ipts_number = ipts_number
        self._exp_number = exp_number
        self._make_paths()
    
    @staticmethod
    def _mkdir_p(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

    def _make_paths(self):
        '''
        Make:
        folder_base
        folder_shared
        folder_datafiles
        '''
        self._folder_base = os.path.abspath(
            os.path.join(
                os.sep,
                'HFIR',
                self._beamline,
                'IPTS-{:04}'.format(self._ipts_number),
                'exp{}'.format(self._exp_number),
            )
        )

        self._folder_shared = os.path.join(self._folder_base, "Shared")
        self._folder_datafiles = os.path.join(self._folder_base, "Datafiles")

        if not os.path.exists(self._folder_base):
            logger.error("The Folder is not valid: %s", self._folder_base)
        if not os.path.exists(self._folder_shared):
            logger.error("The Folder is not valid: %s", self._folder_shared)
        if not os.path.exists(self._folder_datafiles):
            logger.error("The Folder is not valid: %s", self._folder_datafiles)

    def _fullpath(self, scan_number, frame_number):
        '''
        Returns a full path for a datafile for HFIR
        '''
        if self._beamline not in self._instruments.keys():
            logger.error("Beamline not valid.")
        instrument = self._instruments[self._beamline]

        filename = "{}_exp{}_scan{:04}_{:04}.xml".format(
                instrument, self._exp_number, scan_number, frame_number
        )
        filename_path = os.path.join(self._folder_datafiles, filename)
        # Check if file exists:
        if not os.path.exists(filename_path):
            msg = "File does not exist / no permissions to access it: {}"\
                .format(filename_path)
            logger.warning(msg)
            raise IOError(msg)
        return filename_path

    def _hyphen_range(self, s):
        """ Takes a range in form of "a-b" and generate a list of numbers
        between a and b inclusive. Also accepts comma separated ranges like
        "a-b,c-d,f" will build a list which will include numbers from
        a to b, a to d and f"""
        s = "".join(s.split())  # removes white space
        r = set()
        for x in s.split(','):
            t = x.split('-')
            if len(t) not in [1, 2]:
                logger.warning("Hash_range is given its arguement as {}} which seems not correctly formated.".format(s))
            r.add(int(t[0])) if len(t) == 1 else r.update(set(range(int(t[0]), int(t[1]) + 1)))
        l = list(r)
        l.sort()
        #l_in_str = ','.join(str(x) for x in l)
        return l

    def filepath(self, scan_number, frame_number):
        '''
        Returns the full path for a data file
        '''
        return self._fullpath(scan_number, frame_number)

    def range(self, scan_range, frame_range):
        '''
        @param scan_range : must be a string: "1,3,5-10", integer or list
        @param frame_range :  must be a string: "1,3,5-10", integer or list
        '''

        if type(scan_range) == str:
            scan_range = self._hyphen_range(scan_range)
        elif type(scan_range) == int:
            scan_range = [scan_range]
        if type(frame_range) == str:
            frame_range = self._hyphen_range(frame_range)
        elif type(frame_range) == int:
            frame_range = [frame_range]
        res = []

        for s in scan_range:
            for f in frame_range:
                try:
                    res.append(self.filepath(s, f))
                except IOError:
                    # Ignore files that do not exist
                    pass
        return res

    def range_nested(self, scan_range, frame_range):
        '''
        This is used in the same way as range but 
        accepts only lists.
        E.g.

        returns a list of ranges
        '''
        assert type(scan_range) == list
        assert type(frame_range) == list
        assert len(scan_range) == len(frame_range)

        ret = []
        for srange, frange in zip(scan_range, frame_range):
            ret.append(self.range(srange, frange))
        return ret

    def repeat(self, scan_number, frame_number, times=1):
        res = []
        for _ in range(times):
            try:
                res.append(self.filepath(scan_number, frame_number))
            except IOError:
                # Ignore files that do not exist
                pass
        return res

    @property
    def datafiles(self):
        '''
        Returns ./Datafiles absolute path
        '''
        return self._folder_datafiles

    @property
    def base(self):
        '''
        Returns ./ absolute path
        '''
        return self._folder_base

    def shared(self, *paths):
        '''
        Creates folder is it fo
        '''
        fullpath = os.path.join(self._folder_shared, *paths)
        if os.path.exists(fullpath):
            return fullpath
        elif len(paths) >= 1:
            # it doesn't exist
            if '.' in paths[-1]:
                # if last item has . I'm assuming it's a file
                p = os.path.join(self._folder_shared, *(paths[0:-1]))
                self._mkdir_p(p)
            else:
                self._mkdir_p(fullpath)
        return fullpath


class CG2(Experiment):
    def __init__(self, ipts_number, exp_number):
        super(CG2, self).__init__("CG2", ipts_number, exp_number)


class CG3(Experiment):
    def __init__(self, ipts_number, exp_number):
        super(CG3, self).__init__("CG3", ipts_number, exp_number)


class Names(object):
    '''
    '''

    def __init__(self, filepaths, prefix=''):
        '''
        filepaths can be:

        '''
        self.filepaths = filepaths
        self.prefix = prefix
    
    def _parse_single_file(self, filepath):
        '''
        filepath is the form of:
        /HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0030_0002.xml
        returns a dictionary with { scan: frame}
        
        >>> filepath = '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0001.xml'
        >>> n = Names(filepath)
        >>> n._parse_single_file(filepath)
        {'6': '1'}
        '''
        filename = os.path.basename(filepath)
        pattern = r'(?P<prefix>\w+)_exp(?P<exp>\d+)_scan(?P<scan>\d{4})_'\
            '(?P<frame>\d{4}).xml'
        m = re.match(pattern, filename)
        if m:
            scan = int(m.group('scan'))
            frame = int(m.group('frame'))
            return {str(scan): str(frame)}
        else:
            return None
    
    def _parse_multiple_files(self, filepaths):
        '''
        filepaths is a list of filepaths
        returns a dictionary with {scan: (frame1, frame2)}

        >>> filepaths = ['/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0001.xml',
        ... '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0002.xml',
        ... '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0003.xml',
        ... '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0004.xml']
        >>> n = Names(filepaths)
        >>> n._parse_multiple_files(filepaths)
        {'6': ['1', '2', '3', '4']}

        '''
        dd = defaultdict(list)
        for filepath in filepaths:
            d = self._parse_single_file(filepath)
            for key, value in d.iteritems():
                    dd[key].append(value)
        return dict(dd)
    
    def _dict_to_string(self, d):
        '''
        >>> n = Names(None)
        >>> n._dict_to_string({'6': '1'})
        'scan6_frame1'
        >>> n._dict_to_string({'6': ['1', '2', '3', '4']})
        'scan6_frame1-2-3-4'
        >>> n._dict_to_string(OrderedDict({'6': ['1', '2', '3', '4'], 
        ...     '3': ['11', '12', '13', '14']}))
        'scan3_frame11-12-13-14_scan6_frame1-2-3-4'

        >>> n = Names(None,"xpto")
        >>> n._dict_to_string({'6': '1'})
        'xpto_scan6_frame1'
        >>> n._dict_to_string({'6': ['1', '2', '3', '4']})
        'xpto_scan6_frame1-2-3-4'
        '''
        ret = self.prefix + "_" if self.prefix else ''
        for idx, (key, value) in enumerate(d.items()):
            ret += "scan{}_frame{}".format(
                key,
                '-'.join(value)
            )
            if idx != len(d)-1:
                ret += '_'
        return ret

    def parse(self):
        '''
        This is the main method. Use it to transform a file path
        or a list of file paths to a string.

        >>> filepath = '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0001.xml'
        >>> n = Names(filepath)
        >>> n.parse()
        'scan6_frame1'

        >>> filepaths = ['/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0001.xml',
        ... '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0002.xml',
        ... '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0003.xml',
        ... '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0004.xml']
        >>> n = Names(filepaths, "xpto")
        >>> n.parse()
        'xpto_scan6_frame1-2-3-4'

        '''
        if isinstance(self.filepaths, str):
            d = self._parse_single_file(self.filepaths)
            return self._dict_to_string(d)
        elif isinstance(self.filepaths, list):
            d = self._parse_multiple_files(self.filepaths)
            return self._dict_to_string(d)
        else:
            logger.error("Cannot parse: {}".format(self.filepaths))
            return None

#
# Tests
#




class TestCG3(unittest.TestCase):
    '''
    Unit tests
    '''

    def setUp(self):
        self.cg =  CG3(18347, 379)
    
    def tearDown(self):
        # Remove folders created
        shutil.rmtree(self.cg.shared("Ricardo"))

    def test_filepath(self):
        self.assertEqual(self.cg.filepath(10, 1),
            "/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0010_0001.xml")
        # Just to show how to get the file name
        self.assertEqual(os.path.splitext(os.path.basename(
            self.cg.filepath(10, 1)))[0], "BioSANS_exp379_scan0010_0001")
        # Test IPTS starting with a 0
        self.assertEqual(CG2(828,165).filepath(8,1),
            "/HFIR/CG2/IPTS-0828/exp165/Datafiles/CG2_exp165_scan0008_0001.xml")

    def test_ranges(self):
        self.assertEqual(self.cg.range("20,21,24,27-30","1"),
            ['/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0020_0001.xml',
            '/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0021_0001.xml',
            '/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0024_0001.xml',
            '/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0027_0001.xml',
            '/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0028_0001.xml',
            '/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0029_0001.xml',
            '/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0030_0001.xml']
        )
        self.assertEqual(self.cg.range([20,21,24,27,30], "1,2"),
            ['/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0020_0001.xml',
            '/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0021_0001.xml',
            '/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0024_0001.xml',
            '/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0027_0001.xml',
            '/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0030_0001.xml']
        )
        self.assertEqual(self.cg.range(20, 1),
            ['/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0020_0001.xml']
        )

    def test_folders(self):
        self.assertEqual(self.cg.base,"/HFIR/CG3/IPTS-18347/exp379")
        self.assertEqual(self.cg.datafiles,"/HFIR/CG3/IPTS-18347/exp379/Datafiles")
        self.assertEqual(self.cg.shared(),"/HFIR/CG3/IPTS-18347/exp379/Shared")

    def test_make_folders(self):
        self.assertEqual(self.cg.shared("Ricardo"), "/HFIR/CG3/IPTS-18347/exp379/Shared/Ricardo")
        self.assertEqual(self.cg.shared("Ricardo","1","3"), "/HFIR/CG3/IPTS-18347/exp379/Shared/Ricardo/1/3")
        self.assertTrue(os.path.exists(self.cg.shared("Ricardo","1","3")))
        self.assertEqual(self.cg.shared("Ricardo/1/3"), "/HFIR/CG3/IPTS-18347/exp379/Shared/Ricardo/1/3")
        self.assertEqual(self.cg.shared("Ricardo","1","2","file.txt"), "/HFIR/CG3/IPTS-18347/exp379/Shared/Ricardo/1/2/file.txt")
        self.assertTrue(os.path.exists(self.cg.shared("Ricardo","1","2")))
    
    def test_repeat(self):
        self.assertEqual(self.cg.repeat(20,1,5),
            ['/HFIR/CG3/IPTS-18347/exp379/Datafiles/BioSANS_exp379_scan0020_0001.xml'] * 5)


class TestCG2(unittest.TestCase):
    '''
    Unit tests
    '''

    def setUp(self):
        self.cg = CG2(19748, 240)
    
    def tearDown(self):
        pass
    
    def test_range_nested(self):
        self.assertEqual(self.cg.range_nested([5,6,8], [1,"1-4",[1,3,5]]),
            [['/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0005_0001.xml'],
            ['/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0001.xml',
            '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0002.xml',
            '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0003.xml',
            '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0006_0004.xml'],
            ['/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0008_0001.xml',
            '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0008_0003.xml',
            '/HFIR/CG2/IPTS-19748/exp240/Datafiles/CG2_exp240_scan0008_0005.xml']])

if __name__ == "__main__":
    '''
    This will run the tests
    '''
    logging.basicConfig(level=logging.DEBUG)
    print(80*"-")
    print("\t\tDocTest")
    print(80*"-")
    import doctest
    test_result = doctest.testmod(verbose=False)
    
    if test_result.failed == 0:    
        print(80*"-")
        print("\t\tUnitTest")
        print(80*"-")
        unittest.main()
