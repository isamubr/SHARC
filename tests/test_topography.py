#-*- coding: utf-8 -*-
"""
Created on Feb 26 15:08 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import unittest
import os

from sharc.map.topography import Topography


class TopographyTest(unittest.TestCase):

    TEST_VALUES = {
        'low_left': [664740.0, 7799900.0],
        'up_right': [672800.0, 7805440.0],
        'resolution': 20.0,
        'nrows': 276,
        'ncols': 402
    }

    def setUp(self):
        self.our_dir = os.path.dirname(__file__)
        self.topo_file = os.path.join(self.our_dir, 'map_test_files', 'Test_brucutu_res_20m.asc')

    def test_topography_parser(self):

        topo_data = Topography()
        topo_data.parse_raster_data(self.topo_file)
        self.assertEqual(topo_data.nrows, self.TEST_VALUES['nrows'])
        self.assertEqual(topo_data.ncols, self.TEST_VALUES['ncols'])
        self.assertEqual(topo_data.resolution, self.TEST_VALUES['resolution'])
        self.assertEqual(topo_data.low_left, self.TEST_VALUES['low_left'])
        self.assertEqual(topo_data.up_right, self.TEST_VALUES['up_right'])


if __name__ == '__main__':
    unittest.main()

